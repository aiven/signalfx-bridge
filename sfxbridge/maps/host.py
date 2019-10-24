# Copyright 2019, Aiven, https://aiven.io/
#
# mapping rules and constructors for generating the standard
# host metrics signalfx
#
from .metrics import Constructors, DataPointType, Mappings

Mappings.register(
    mapping={
        "net": {
            "bytes_recv": {
                "name": "if_octets.rx",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "net-io"),
                    ("plugin_instance", "$interface"),
                ],
            },
            "bytes_sent": {
                "name": "if_octets.tx",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "net-io"),
                    ("plugin_instance", "$interface"),
                ],
            },
            "err_in": {
                "name": "if_errors.rx",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "net-io"),
                    ("plugin_instance", "$interface"),
                ],
            },
            "err_out": {
                "name": "if_errors.tx",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "net-io"),
                    ("plugin_instance", "$interface"),
                ],
            },
        },
        "swap": {
            "in": {
                "name": "vmpage_io.swap.in",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "vmem"),
                ],
            },
            "out": {
                "name": "vmpage_io.swap.out",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "vmem"),
                ],
            },
        },
        "system": {
            "load1": {
                "name": "load.shortterm",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "load"),
                ],
            },
            "load15": {
                "name": "load.longterm",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "load"),
                ],
            },
            "load5": {
                "name": "load.midterm",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "load"),
                ],
            },
        },
        "mem": {
            "inactive": {
                "name": "memory.inactive",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "memory"),
                ],
            },
            "active": {
                "name": "memory.active",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "memory"),
                ],
            },
            "wired": {
                "name": "memory.wired",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "memory"),
                ],
            },
            "used": {
                "name": "memory.used",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "memory"),
                ],
            },
            "buffered": {
                "name": "memory.buffered",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "memory"),
                ],
            },
            "cached": {
                "name": "memory.cached",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "memory"),
                ],
            },
            "free": {
                "name": "memory.free",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "memory"),
                ],
            },
            "used_percent": {
                "name": "memory.utilization",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "signalfx-metadata"),
                ],
            }
        },
        "disk": {
            "free": {
                "name": "df_complex.free",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "df"),
                    ("plugin_instance", "data"),
                ],
            },
            "used": {
                "name": "df_complex.used",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "df"),
                    ("plugin_instance", "data"),
                ],
            },
            "used_percent": {
                "name": "disk.utilization",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "signalfx-metadata"),
                    ("plugin_instance", "data"),
                ],
            },
        },
        "diskio": {
            "reads": {
                "name": "disk_ops.read",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "disk-io"),
                ],
            },
            "writes": {
                "name": "disk_ops.write",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("plugin", "disk-io"),
                ],
            },
        },
    }
)


@Constructors.register
class _CpuUtilization:
    """
    Maps and "calculates" the total cpu utilization
    """

    class Meta:
        mappings = {
            "_constructed_cpu_utilization": {
                "utilization": {
                    "name": "cpu.utilization",
                    "type": DataPointType.gauge,
                    "dimensions": [("host", "$host"), ("cluster", "$service"), ("plugin", "signalfx-metadata")],
                },
            },
        }

    metrics = None

    def __init__(self):
        self.clear()

    def clear(self):
        self.metrics = []

    def process(self, metric):
        if metric.get("name") != "cpu":
            return

        if metric.get("tags", {}).get("cpu") != "cpu-total":
            return

        result = {
            "name": "_constructed_cpu_utilization",
            "tags": metric.get("tags"),
            "fields": {
                "utilization": round(100.0 - metric["fields"].get("usage_idle", 0.0), 2),
            },
            "timestamp": metric.get("timestamp")
        }

        self.metrics.append(result)


@Constructors.register
class _NetworkTotal:
    """
    Maps and "calculates" the total network traffic
    """

    class Meta:
        mappings = {
            "_constructed_network_total": {
                "total": {
                    "name": "network.total",
                    "type": DataPointType.counter,
                    "dimensions": [
                        ("host", "$host"),
                        ("cluster", "$service"),
                    ],
                },
            },
        }

    _metrics = None
    _interfaces = None
    _tags = None
    _timestamp = None

    def __init__(self):
        self.clear()

    def clear(self):
        self._metrics = []
        self._interfaces = {}
        self._tags = None

    @property
    def metrics(self):
        total_bytes = 0
        for value in self._interfaces.values():
            total_bytes += value

        if not total_bytes:
            return []

        result = {
            "name": "_constructed_network_total",
            "tags": self._tags,
            "fields": {
                "total": total_bytes,
            },
            "timestamp": self._timestamp,
        }
        return [result]

    def process(self, metric):
        if metric.get("name") != "net":
            return

        if self._tags is None:
            self._tags = metric.get("tags")

        # Only report for individual interfaces
        interface = metric.get("tags", {}).get("interface", "all")
        if interface == "all":
            return

        if self._timestamp is None:
            self._timestamp = metric.get("timestamp")

        in_bytes = metric.get("fields", {}).get("bytes_recv", 0)
        out_bytes = metric.get("fields", {}).get("bytes_sent", 0)

        self._interfaces[interface] = in_bytes + out_bytes
