# Copyright 2019, Aiven, https://aiven.io/
from logging import getLogger

from sfxbridge.mapper import Mapper
from sfxbridge.maps.metrics import DataPointType

log = getLogger(__name__)

KAFKA_METRICS = [
    {
        "fields": {
            "Count": 717688622
        },
        "name": "kafka.server:BrokerTopicMetrics.BytesInPerSec",
        "tags": {
            "cloud": "google-europe-west1",
            "host": "k1-3",
            "project": "aiven-system-services",
            "service": "k1",
            "service_type": "kafka"
        },
        "timestamp": 1571666310
    },
    {
        "fields": {
            "Count": 809457929
        },
        "name": "kafka.server:BrokerTopicMetrics.BytesOutPerSec",
        "tags": {
            "cloud": "google-europe-west1",
            "host": "k1-3",
            "project": "aiven-system-services",
            "service": "k1",
            "service_type": "kafka"
        },
        "timestamp": 1571666310
    },
    {
        "fields": {
            "Count": 717688622
        },
        "name": "kafka.server:BrokerTopicMetrics.BytesInPerSec",
        "tags": {
            "cloud": "google-europe-west1",
            "host": "k1-3",
            "project": "aiven-system-services",
            "service": "k1",
            "service_type": "kafka",
            "topic": "foo-topic",
        },
        "timestamp": 1571666310
    },
    {
        "fields": {
            "Count": 809457929
        },
        "name": "kafka.server:BrokerTopicMetrics.BytesOutPerSec",
        "tags": {
            "cloud": "google-europe-west1",
            "host": "k1-3",
            "project": "aiven-system-services",
            "service": "k1",
            "service_type": "kafka",
            "topic": "foo-topic",
        },
        "timestamp": 1571666310
    },
    {
        "fields": {
            "Count": 3473961
        },
        "name": "kafka.server:BrokerTopicMetrics.MessagesInPerSec",
        "tags": {
            "cloud": "google-europe-west1",
            "host": "k1-3",
            "project": "aiven-system-services",
            "service": "k1",
            "service_type": "kafka"
        },
        "timestamp": 1571666310
    },
    {
        "fields": {
            "Count": 3473961
        },
        "name": "kafka.server:BrokerTopicMetrics.MessagesInPerSec",
        "tags": {
            "cloud": "google-europe-west1",
            "host": "k1-3",
            "project": "aiven-system-services",
            "service": "k1",
            "service_type": "kafka",
            "topic": "foo-topic",
        },
        "timestamp": 1571666310
    },
    {
        "fields": {
            "95thPercentile": 501,
            "Count": 1246480,
            "Mean": 326.74261440215645
        },
        "name": "kafka.network:RequestMetrics.TotalTimeMs",
        "tags": {
            "cloud": "google-europe-west1",
            "host": "k1-3",
            "project": "aiven-system-services",
            "request": "FetchConsumer",
            "service": "k1",
            "service_type": "kafka"
        },
        "timestamp": 1571666310
    },
    {
        "fields": {
            "95thPercentile": 502,
            "Count": 1932488,
            "Mean": 397.2585371810847
        },
        "name": "kafka.network:RequestMetrics.TotalTimeMs",
        "tags": {
            "cloud": "google-europe-west1",
            "host": "k1-3",
            "project": "aiven-system-services",
            "request": "FetchFollower",
            "service": "k1",
            "service_type": "kafka"
        },
        "timestamp": 1571666310
    },
    {
        "fields": {
            "95thPercentile": 3,
            "Count": 299815,
            "Mean": 1.7560395577272652
        },
        "name": "kafka.network:RequestMetrics.TotalTimeMs",
        "tags": {
            "cloud": "google-europe-west1",
            "host": "k1-3",
            "project": "aiven-system-services",
            "request": "Produce",
            "service": "k1",
            "service_type": "kafka"
        },
        "timestamp": 1571666310
    },
]


# Test constructed metrics
def test_bytes_in_out():
    mapper = Mapper(log=log, whitelist=["counter.kafka-bytes-in", "counter.kafka-bytes-out"], service="kafka")
    mapper.process(KAFKA_METRICS)
    assert mapper.datapoints == {
        DataPointType.cumulative: [
            {
                "dimensions": {
                    "cluster": "k1",
                    "host": "k1-3",
                    "hostHasService": "kafka",
                },
                "metric": "counter.kafka-bytes-in",
                "value": 717688622,
                "timestamp": 1571666310000,
            },
            {
                "dimensions": {
                    "cluster": "k1",
                    "host": "k1-3",
                    "hostHasService": "kafka",
                },
                "metric": "counter.kafka-bytes-out",
                "value": 809457929,
                "timestamp": 1571666310000,
            },
        ]
    }


def test_messages_in():
    mapper = Mapper(log=log, whitelist=["counter.kafka-messages-in"], service="kafka")
    mapper.process(KAFKA_METRICS)
    assert mapper.datapoints == {
        DataPointType.cumulative: [
            {
                "dimensions": {
                    "cluster": "k1",
                    "host": "k1-3",
                    "hostHasService": "kafka"
                },
                "metric": "counter.kafka-messages-in",
                "value": 3473961,
                "timestamp": 1571666310000,
            },
        ]
    }


def test_request_metrics():
    mapper = Mapper(
        log=log,
        whitelist=[
            "counter.kafka.fetch-consumer.total_time.count",
            "counter.kafka.fetch-follower.total_time.count",
            "counter.kafka.produce.total_time.count",
        ],
        service="kafka",
    )
    mapper.process(KAFKA_METRICS)
    assert mapper.datapoints == {
        DataPointType.cumulative: [
            {
                "dimensions": {
                    "cluster": "k1",
                    "host": "k1-3",
                    "hostHasService": "kafka",
                },
                "metric": "counter.kafka.fetch-consumer.total_time.count",
                "value": 1246480,
                "timestamp": 1571666310000,
            },
            {
                "dimensions": {
                    "cluster": "k1",
                    "host": "k1-3",
                    "hostHasService": "kafka",
                },
                "metric": "counter.kafka.fetch-follower.total_time.count",
                "value": 1932488,
                "timestamp": 1571666310000,
            },
            {
                "dimensions": {
                    "cluster": "k1",
                    "host": "k1-3",
                    "hostHasService": "kafka",
                },
                "metric": "counter.kafka.produce.total_time.count",
                "value": 299815,
                "timestamp": 1571666310000,
            },
        ],
    }
