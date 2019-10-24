# Copyright 2019, Aiven, https://aiven.io/
from typing import Any, List, Optional, Set

from . import maps


class Mapper:
    """
    Handles mapping of telegraf values to signalfx datapoints by
    mapping telegraf metrics to signalfx metrics based on simple
    conversion table and "constructors" operating over all received
    telegraf metrics
    """

    datapoints = None

    @classmethod
    def supported_datapoints(cls: "Mapper", service: Optional[str] = None) -> List[str]:
        mappings, _ = maps.get_rules(service=service)
        dps = set()
        for conversion in mappings.values():
            for dp in conversion.values():
                dps.add(dp["name"])
        return list(dps)

    def __init__(self, *, log, whitelist: Set[str], service: str):
        self.log = log
        self._whitelist = whitelist
        self._mappings, constructors = maps.get_rules(service=service)
        self._collectors = [cls() for cls in constructors]
        self.clear()

    def clear(self):
        self.datapoints = {}
        for collector in self._collectors:
            collector.clear()

    def process(self, metrics: List[dict]):
        for metric in metrics:
            self._simple_mapping(metric)
            for collector in self._collectors:
                collector.process(metric)

        for collector in self._collectors:
            for metric in collector.metrics:
                self._simple_mapping(metric)

    def _simple_mapping(self, metric: dict) -> None:
        name = metric.get("name")
        fields = metric.get("fields", {})
        timestamp = metric.get("timestamp")

        conversion = self._mappings.get(name)
        if not conversion:
            return

        for field, value in fields.items():
            if field not in conversion:
                continue

            dp_name = conversion[field]["name"]
            if dp_name not in self._whitelist:
                continue

            dp_type = conversion[field]["type"]
            dp_dimensions = self._get_dimensions(conversion[field]["dimensions"], metric)
            self._new_datapoint(
                dp_type=dp_type,
                name=dp_name,
                value=value,
                dimensions=dp_dimensions,
                timestamp=timestamp,
            )

    def _get_dimensions(self, dimensions: List[str], metric: dict) -> dict:
        d = {}
        tags = metric.get("tags")
        if not tags:
            self.log.warning("Missing tags for metric %r", metric)
            tags = {}
        for dimension in dimensions:
            key = dimension[0]
            value = dimension[1]

            # values starting '$' are references to origina metric tags
            if value[0] == "$":
                value = tags.get(value[1:])

            if not value:
                self.log.warning('Unknown dimension "%s" requested', dimension)
                continue

            d[key] = value
        return d

    def _new_datapoint(
        self,
        *,
        dp_type: maps.DataPointType,
        name: str,
        value: Any,
        dimensions: dict,
        timestamp: Optional[int] = None,
    ) -> None:
        dp = {
            "metric": name,
            "value": value,
            "dimensions": dimensions,
        }
        if timestamp:
            dp["timestamp"] = timestamp * 1000  # telegraf timestamps are in seconds

        if dp_type not in self.datapoints:
            self.datapoints[dp_type] = []
        self.datapoints[dp_type].append(dp)
