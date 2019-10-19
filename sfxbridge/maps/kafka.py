# Copyright 2019, Aiven, https://aiven.io/
#
# mapping rules and constructors for generating kafka metrics for signalfx
#
from .metrics import Constructors, DataPointType, Mappings

Mappings.register(
    service="kafka",
    mapping={
        "kafka.server:ReplicaManager.IsrExpandsPerSec": {
            "Count": {
                "name": "counter.kafka-isr-expands",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("hostHasService", "kafka"),
                ],
            },
        },
        "kafka.server:ReplicaManager.IsrShrinksPerSec": {
            "Count": {
                "name": "counter.kafka-isr-shrinks",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("hostHasService", "kafka"),
                ],
            },
        },
        "kafka.controller:ControllerStats.LeaderElectionRateAndTimeMs": {
            "Count": {
                "name": "counter.kafka-leader-election-rate",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("hostHasService", "kafka"),
                ],
            },
        },
        "kafka.controller:ControllerStats.UncleanLeaderElectionsPerSec": {
            "Count": {
                "name": "counter.kafka-unclean-election-rate",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("hostHasService", "kafka"),
                ],
            },
        },
        "kafka.log:LogFlushStats.LogFlushRateAndTimeMs": {
            "Count": {
                "name": "counter.kafka.logs.flush-time.count",
                "type": DataPointType.cumulative,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("hostHasService", "kafka"),
                ],
            }
        },
        "kafka.controller:KafkaController.ActiveControllerCount": {
            "Value": {
                "name": "gauge.kafka-active-controllers",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("hostHasService", "kafka"),
                ],
            }
        },
        "kafka.controller:KafkaController.OfflinePartitionsCount": {
            "Value": {
                "name": "gauge.kafka-offline-partitions-count",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("hostHasService", "kafka"),
                ],
            }
        },
        "kafka.server:ReplicaManager.UnderReplicatedPartitions": {
            "Value": {
                "name": "gauge.kafka-underreplicated-partitions",
                "type": DataPointType.gauge,
                "dimensions": [
                    ("host", "$host"),
                    ("cluster", "$service"),
                    ("hostHasService", "kafka"),
                ],
            }
        },
    }
)


@Constructors.register(service="kafka")
class KafkaBytesInOut:
    class Meta:
        mappings = {
            "counter.kafka_bytes": {
                "in": {
                    "name": "counter.kafka-bytes-in",
                    "type": DataPointType.cumulative,
                    "dimensions": [
                        ("host", "$host"),
                        ("cluster", "$service"),
                        ("hostHasService", "kafka"),
                    ],
                },
                "out": {
                    "name": "counter.kafka-bytes-out",
                    "type": DataPointType.cumulative,
                    "dimensions": [
                        ("host", "$host"),
                        ("cluster", "$service"),
                        ("hostHasService", "kafka"),
                    ],
                },
            },
        }

    _tags = None
    _bytes = None

    def __init__(self):
        self.clear()

    def clear(self):
        self._tags = None
        self._bytes = {"in": 0, "out": 0}

    @property
    def metrics(self):
        fields = {}
        if self._bytes["in"]:
            fields["in"] = self._bytes["in"]
        if self._bytes["out"]:
            fields["out"] = self._bytes["out"]
        if not fields:
            return []

        return [{
            "name": "counter.kafka_bytes",
            "tags": self._tags,
            "fields": fields,
        }]

    def process(self, metric):
        """
        Constucts total number of bytes in/out
        """
        name = metric.get("name")
        if name not in {"kafka.server:BrokerTopicMetrics.BytesInPerSec", "kafka.server:BrokerTopicMetrics.BytesOutPerSec"}:
            return
        if self._tags is None:
            self._tags = metric.get("tags")
        count = metric["fields"].get("Count", 0)
        if name == "kafka.server:BrokerTopicMetrics.BytesInPerSec":
            self._bytes["in"] += count
        else:
            self._bytes["out"] += count


@Constructors.register(service="kafka")
class KafkaMessagesIn:
    class Meta:
        mappings = {
            "_total_kafka_messages_in": {
                "Count": {
                    "name": "counter.kafka-messages-in",
                    "type": DataPointType.cumulative,
                    "dimensions": [
                        ("host", "$host"),
                        ("cluster", "$service"),
                        ("hostHasService", "kafka"),
                    ],
                }
            }
        }

    metrics = None

    def __init__(self):
        self.clear()

    def clear(self):
        self.metrics = []

    def process(self, metric):
        """
        Filter out topic specific stats (total is the one without topic)
        """
        name = metric.get("name")
        if name != "kafka.server:BrokerTopicMetrics.MessagesInPerSec":
            return

        tags = metric.get("tags")
        if tags.get("topic"):
            return

        self.metrics.append({"name": "_total_kafka_messages_in", "tags": tags, "fields": metric["fields"]})


@Constructors.register(service="kafka")
class RequestMetrics:
    class Meta:
        mappings = {
            "_constructed_kafka_fetch": {
                "fetch-consumer": {
                    "name": "counter.kafka.fetch-consumer.total_time.count",
                    "type": DataPointType.cumulative,
                    "dimensions": [
                        ("host", "$host"),
                        ("cluster", "$service"),
                        ("hostHasService", "kafka"),
                    ],
                },
                "fetch-follower": {
                    "name": "counter.kafka.fetch-follower.total_time.count",
                    "type": DataPointType.cumulative,
                    "dimensions": [
                        ("host", "$host"),
                        ("cluster", "$service"),
                        ("hostHasService", "kafka"),
                    ],
                },
                "produce": {
                    "name": "counter.kafka.produce.total_time.count",
                    "type": DataPointType.cumulative,
                    "dimensions": [
                        ("host", "$host"),
                        ("cluster", "$service"),
                        ("hostHasService", "kafka"),
                    ],
                }
            }
        }

    metrics = None

    def __init__(self):
        self.clear()

    def clear(self):
        self.metrics = []

    def process(self, metric):
        name = metric.get("name")
        if name != "kafka.network:RequestMetrics.TotalTimeMs":
            return

        field = None

        tags = metric.get("tags")
        request = tags.get("request")
        if request == "FetchConsumer":
            field = "fetch-consumer"
        elif request == "FetchFollower":
            field = "fetch-follower"
        elif request == "Produce":
            field = "produce"

        if field is None:
            return

        if not self.metrics:
            self.metrics.append({
                "name": "_constructed_kafka_fetch",
                "tags": tags,
                "fields": {},
            })
        self.metrics[0]["fields"][field] = metric["fields"].get("Count")
