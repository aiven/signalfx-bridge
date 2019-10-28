# Copyright 2019, Aiven, https://aiven.io/
#
# This file is under the Apache License, Version 2.0.
# See the file `LICENSE` for details.
#
# sfxbridge receives telegraf metrics via http/out and
# converts datapoints and sends them to signalfx via the ingres API.
#
import datetime
import fnmatch
import json
import logging
from queue import Full, Queue
from threading import Thread

import requests
import systemd.daemon
from aiohttp import web

from .mapper import Mapper


class _HttpServer:
    def __init__(self, *, config):
        super().__init__()
        self.config = config
        self.log = logging.getLogger("_HttpServer")
        self.log.setLevel(self.config.get("log_level", "WARNING"))
        self._status = {
            "started": None,
        }

    async def get_status(self, _) -> web.Response:
        """handler for GET. Returns the current status of the sfxbridge"""
        return web.json_response(self._status)

    async def send_metrics(self, request: web.Request) -> web.Response:
        """handler for POST from telegraf http output

        The request body is assumed to be json format, if it is successfully
        decoded, puts the resulting dict to queue for processing and forwarding
        to SignalFX by SfxClient. The queue will only buffer on telegraf POST
        worth of data, if more data is received before the previous has been
        processed the new data is skipped.
        """
        data = await request.json()
        # If the queue is full just drop the metrics
        try:
            request.app["sfx_queue"].put(data, False, 0)
        except Full:
            self.log.warning("Overrun, skipping latest metrics")
        return web.Response()

    def update_status(self, key, value):
        self._status[key] = value


class SfxClient:
    def __init__(self, *, config, queue, server):
        super().__init__()
        self.queue = queue
        self.config = config
        self.server = server
        self.service = self.config.get("service")
        self.log = logging.getLogger("SfxClient")
        self.log.setLevel(self.config.get("log_level", "WARNING"))
        self._stop_requested = False
        self._url = None
        self._realm = self.config.get("realm")
        self._apikey = self.config.get("apikey")
        if self._realm:
            self._url = f"https://ingest.{self._realm}.signalfx.com/v2/datapoint"
        else:
            self.log.error("No realm given, no metrics will be sent")
        self._headers = {"Content-Type": "application/json"}
        if self._apikey:
            self._headers["X-SF-TOKEN"] = self._apikey
        self._timeout = self.config.get("timeout", 20.0)
        self._trace = self.config.get("trace", False)

        # Whitelist determines which statistics are actually send, even though
        # the configuration has a list of glob patterns
        self.whitelist = set()
        datapoints = Mapper.supported_datapoints(service=self.service)
        for pattern in self.config.get("whitelist", ["*"]):  # default is to send everything
            for dp in fnmatch.filter(datapoints, pattern):
                self.whitelist.add(dp)

        self._mapper = Mapper(log=self.log, whitelist=self.whitelist, service=self.service)

    def stop(self) -> None:
        """Stop the sender (running in a separate thread)"""
        # Already stopped?
        if self._stop_requested:
            return

        self._stop_requested = True
        self.server.update_status("state", "stopping")
        # In case the actual sender thread is waiting for metrics
        # trigger it by sending empty "metrics"
        try:
            self.queue.put({}, False, 0)
        except Full:
            pass

    def run(self) -> None:
        """
        Run the sender, this runs as a separate thread (started by
        SfxBridge.run() and basically waits for a telegraf metrics
        from the queue, converts it to SignalFX datapoint format and
        sends it to SignalFX via their REST api. There is no retry
        and send failures result in datapoints being dropped.
        """
        self.server.update_status("state", "starting")
        while not self._stop_requested:
            data = self.queue.get()

            if self._stop_requested:
                return
            try:
                self.process(data)
            except Exception:  # pylint: disable=broad-except
                self.log.exception("Failed to process metrics")
                self.server.update_status("state", "internal error")

    def process(self, data: dict) -> None:
        """Process the telegraf data"""
        try:
            metrics = data["metrics"]
        except KeyError:
            self.log.debug("Received data without metrics")
            return

        self._mapper.clear()
        self._mapper.process(metrics)
        self.send(self._mapper.datapoints)

        if self._trace:
            with open("trace.json", "a") as fp:
                print("\nTELEGRAF DATA\n", file=fp)
                json.dump(metrics, fp=fp, indent=2)
                print("\nDATAPOINTS\n", file=fp)
                json.dump(self._mapper.datapoints, fp=fp, indent=2)

    def send(self, points: dict):
        if not points:
            self.log.debug("No data")
            return

        if self._url:
            try:
                resp = requests.post(self._url, data=json.dumps(points), headers=self._headers, timeout=self._timeout)
            except requests.exceptions.RequestException as ex:
                self.log.warning('Failed to connect "%s" (%r)', self._url, ex)
                self.server.update_status("state", "disconnected")
                return

            self.server.update_status("http-status", resp.status_code)
            if resp.status_code not in {200, 204}:
                self.log.warning("Failed to send metric: %r", resp)
                self.server.update_status("state", "disconnected")

            self.server.update_status("state", "connected")


class SfxBridge:
    def __init__(self, *, config):
        super().__init__()
        self.config = config

        server = _HttpServer(config=config)
        server.update_status("started", datetime.datetime.utcnow().isoformat())

        queue = Queue(maxsize=1)
        sfx_client = SfxClient(config=config, queue=queue, server=server)

        self._client = Thread(target=sfx_client.run)

        self.app = web.Application()
        self.app.add_routes([
            web.get("/", server.get_status),
            web.post("/", server.send_metrics),
            web.put("/", server.send_metrics),
        ])

        self.app["sfx_queue"] = queue
        self.app["sfx_client"] = sfx_client

        if self.config.get("daemon", True):

            async def systemd_daemon_notify(_):
                systemd.daemon.notify("READY=1")

            self.app.on_startup.append(systemd_daemon_notify)

        async def stop_sender(app):
            app["sfx_client"].stop()

        self.app.on_shutdown.append(stop_sender)

    def run(self):
        self._client.start()
        web.run_app(self.app, host=self.config["host"], port=self.config["port"], access_log=None)
        self._client.join()

    @classmethod
    def run_exit(cls, config):
        cls(config=config).run()
