# Copyright 2019, Aiven, https://aiven.io/
from logging import getLogger

from sfxbridge.mapper import Mapper
from sfxbridge.maps.metrics import DataPointType

log = getLogger(__name__)


def test_simple_mapping():
    mapper = Mapper(log=log, whitelist=["load.midterm"], service=None)
    mapper.process([
        {
            "fields": {
                "load1": 0.54,
                "load15": 0.23,
                "load5": 0.47,
                "n_cpus": 1,
                "n_users": 1
            },
            "name": "system",
            "tags": {
                "cloud": "google-europe-north1",
                "host": "pg-2",
                "project": "test",
                "service": "pg",
                "service_type": "pg"
            },
            "timestamp": 1570444470
        },
    ])
    assert mapper.datapoints == {
        DataPointType.gauge: [{
            "dimensions": {
                "cluster": "pg",
                "host": "pg-2",
                "plugin": "load",
            },
            "metric": "load.midterm",
            "value": 0.47,
            "timestamp": 1570444470000,
        }]
    }


# Test constructed metrics
def test_cpu_utilization():
    mapper = Mapper(log=log, whitelist=["cpu.utilization"], service=None)
    mapper.process([
        {
            "fields": {
                "usage_guest": 0,
                "usage_guest_nice": 0,
                "usage_idle": 90.9303101033699,
                "usage_iowait": 1.4671557185728608,
                "usage_irq": 0.26675558519508497,
                "usage_nice": 0,
                "usage_softirq": 0.13337779259753063,
                "usage_steal": 0,
                "usage_system": 2.4341447149050466,
                "usage_user": 4.768256085361656
            },
            "name": "cpu",
            "tags": {
                "cloud": "google-europe-north1",
                "cpu": "cpu-total",
                "host": "pg-2",
                "project": "test",
                "service": "pg",
                "service_type": "pg"
            },
            "timestamp": 1570444500
        },
    ])
    assert mapper.datapoints == {
        DataPointType.gauge: [{
            "dimensions": {
                "cluster": "pg",
                "host": "pg-2",
                "plugin": "signalfx-metadata",
            },
            "metric": "cpu.utilization",
            "value": 9.07,
            "timestamp": 1570444500000,
        }]
    }


def test_network_total():
    mapper = Mapper(log=log, whitelist=["network.total"], service=None)
    mapper.process([
        {
            "fields": {
                "bytes_recv": 156796692,
                "bytes_sent": 24029619,
                "drop_in": 0,
                "drop_out": 0,
                "err_in": 0,
                "err_out": 0,
                "packets_recv": 168056,
                "packets_sent": 100486
            },
            "name": "net",
            "tags": {
                "cloud": "google-europe-north1",
                "host": "pg-2",
                "interface": "eth0",
                "project": "test",
                "service": "pg",
                "service_type": "pg"
            },
            "timestamp": 1570444500
        },
        {
            "fields": {
                "icmp_inaddrmaskreps": 0,
                "icmp_inaddrmasks": 0,
                "udplite_outdatagrams": 0,
                "udplite_rcvbuferrors": 0,
                "udplite_sndbuferrors": 0
            },
            "name": "net",
            "tags": {
                "cloud": "google-europe-north1",
                "host": "pg-2",
                "interface": "all",
                "project": "test",
                "service": "pg",
                "service_type": "pg"
            },
            "timestamp": 1570444500,
        },
    ])
    assert mapper.datapoints == {
        DataPointType.counter: [{
            "dimensions": {
                "cluster": "pg",
                "host": "pg-2",
            },
            "metric": "network.total",
            "value": 156796692 + 24029619,
            "timestamp": 1570444500000,
        }]
    }
