# Copyright 2019, Aiven, https://aiven.io/
from sfxbridge.sfxbridge import SfxClient


def test_default_whitelist():
    sfxclient = SfxClient(server=None, queue=None, config={"realm": "foo"})
    assert sfxclient.whitelist


def test_configured_whitelist():
    sfxclient = SfxClient(server=None, queue=None, config={"realm": "foo", "whitelist": ["load.*"]})
    assert sfxclient.whitelist == {"load.shortterm", "load.longterm", "load.midterm"}


def test_service_whitelist():
    sfxclient = SfxClient(server=None, queue=None, config={"realm": "foo", "service": "kafka"})
    assert "gauge.kafka-underreplicated-partitions" in sfxclient.whitelist
