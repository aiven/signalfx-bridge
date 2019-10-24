# Copyright 2019, Aiven, https://aiven.io/
#
# Helpers for registering and accessing the mappers and contructors
#
from enum import Enum
from functools import partial
from typing import Any, Optional


class DataPointType(str, Enum):
    gauge = "gauge"
    counter = "counter"
    cumulative = "cumulative_counter"


DEFAULT_MAPPING = "__all__"


class Mappings:
    mappings = {}

    @classmethod
    def register(cls, *, mapping: dict, service: Optional[str] = None) -> None:
        if service is None:
            service = DEFAULT_MAPPING
        if service not in cls.mappings:
            cls.mappings[service] = {}
        cls.mappings[service].update(mapping)


class Constructors:
    constructors = {}

    @classmethod
    def register(cls, arg: Optional[Any] = None, service: Optional[str] = None):
        def fn(constructor, *, cls, service):
            Mappings.register(service=service, mapping=constructor.Meta.mappings)
            if service not in cls.constructors:
                cls.constructors[service] = []
            cls.constructors[service].append(constructor)
            return constructor

        if service is None:
            return fn(arg, cls=cls, service=DEFAULT_MAPPING)
        return partial(fn, cls=cls, service=service)


def get_rules(*, service: Optional[str] = None):
    mappings = Mappings.mappings[DEFAULT_MAPPING]
    constructors = Constructors.constructors[DEFAULT_MAPPING]
    if service is not None:
        mappings.update(Mappings.mappings[service])
        constructors += Constructors.constructors[service]

    return (mappings, constructors)
