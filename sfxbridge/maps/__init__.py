# Copyright 2019, Aiven, https://aiven.io/
__all__ = ["host", "kafka", "get_rules", "DataPointType"]

# Import the known mappings to have them registered
#
# Mappings are either simple dictionaries with entries:
# { "<TELEGRAF_MODULE">:
#     "<TELEGRAF_FIELD>": {
#         "name": "<SIGNALFX_METRICS_NAME>",
#         "type": DataPointType,
#         "dimensions": <list-of-dimension-mappings>,
#     }
# }
# Where type can be either gauge, counter or cumulative
# dimension mapping is a tuple where the first item is
# the name of the dimension and second item is the value
# if the value starts with $ it is taken from the field
# of the telegraf metric. E.g. ("host", "$host")
#
# An alternatively the signalfx metric can be constructed
# This is done by registering a class that will be instantiated
# for each received set of telegraf metrics and method
# process() called for each metric in the batch. Once all
# metrics have been processed, the instance poperty metrics
# is called and processes using the same mapping rules as
# before. The class must define the mapping rule in
# Meta.mapping using the normal mapping rule syntax.
#
from . import host
from . import kafka

from .metrics import get_rules, DataPointType
