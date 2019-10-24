# Copyright 2019, Aiven, https://aiven.io/
#
# This file is under the Apache License, Version 2.0.
# See the file `LICENSE` for details.
import argparse
import json
import logging
import os
import sys

from . import sfxbridge

LOG_FORMAT_JOURNAL = "%(name)-20s  %(levelname)-8s  %(message)s"


def main():
    logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT_JOURNAL)
    log = logging.getLogger(__name__)

    parser = argparse.ArgumentParser("Telegraf to SignalFX bridge")
    parser.add_argument("--config", required=True, metavar="FILE", help="configuration file to use")
    args = parser.parse_args()

    config_file = args.config
    if not os.path.isfile(config_file):
        log.fatal('Could not read config file "%s"', config_file)
        sys.exit(2)

    config = None
    try:
        with open(config_file, "r") as fp:
            config = json.load(fp)
    except Exception:  # pylint: disable=broad-except
        log.exception('Error reading config file "%s"', config_file)
        sys.exit(2)

    sfxbridge.SfxBridge.run_exit(config)


if __name__ == "__main__":
    main()
