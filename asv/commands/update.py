# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from . import Command
from ..config import Config
from ..machine import Machine, MachineCollection
from ..results import Results
from ..benchmarks import Benchmarks
from ..console import log
from .. import util
from .run import Run


class Update(Command):
    @classmethod
    def setup_arguments(cls, subparsers):
        parser = subparsers.add_parser(
            "update", help="Update the results and config files "
            "to the current version",
            description="Update the results and config files "
            "to the current version")

        parser.set_defaults(func=cls.run_from_args)

        return parser

    @classmethod
    def run_from_args(cls, args):
        return cls.run(args.config)

    @classmethod
    def run(cls, config_path):
        MachineCollection.update()
        Config.update(config_path)

        conf = Config.load(config_path)

        log.info("Updating results data...")

        for root, dirs, files in os.walk(conf.results_dir):
            for filename in files:
                path = os.path.join(root, filename)
                if filename == 'machine.json':
                    Machine.update(path)
                elif filename == "benchmarks.json":
                    pass
                elif filename.endswith('.json'):
                    Results.update(path)

        # Check benchmarks.json
        log.info("Updating benchmarks.json...")
        ok = False
        try:
            Benchmarks.load(conf)
            ok = True
        except util.UserError:
            pass

        if not ok:
            # Regenerating the file is needed
            with log.indent():
                Run.run(conf, bench=['just-discover'])
