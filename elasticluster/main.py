#! /usr/bin/env python
#
#   Copyright (C) 2013 GC3, University of Zurich
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
__author__ = 'Nicolas Baer <nicolas.baer@uzh.ch>'

# System imports
import logging
import os
import shutil
import sys

# External modules
import cli.app

# Elasticluster imports
from elasticluster import log
from elasticluster.subcommands import Start, SetupCluster
from elasticluster.subcommands import Stop
from elasticluster.subcommands import AbstractCommand
from elasticluster.subcommands import ListClusters
from elasticluster.subcommands import ListNodes
from elasticluster.subcommands import ResizeCluster
from elasticluster.subcommands import SshFrontend
from elasticluster.conf import Configuration


class ElasticCloud(cli.app.CommandLineApp):

    name = "elasticluster"

    default_configuration_file = os.path.expanduser(
        "~/.elasticluster/config.cfg")
    default_storage_dir = os.path.expanduser(
        "~/.elasticluster/storage")

    def setup(self):
        cli.app.CommandLineApp.setup(self)

        # all commands in this list will be added to the subcommands
        # if you add an object here, make sure it implements the
        # subcommands.abstract_command contract
        commands = [Start(self.params),
                    Stop(self.params),
                    ListClusters(self.params),
                    ListNodes(self.params),
                    SetupCluster(self.params),
                    ResizeCluster(self.params),
                    SshFrontend(self.params),
                    ]

        # global parameters
        self.add_param('-v', '--verbose', action='count', default=0,
                       help="Increase verbosity.")
        self.add_param('-s', '--storage', metavar="PATH",
                       help="Path to the storage folder. Default: `%s`" %
                       self.default_storage_dir,
                       default=self.default_storage_dir)
        self.add_param('-c', '--config', metavar='PATH',
                       help="Path to the configuration file. Default: `%s`" %
                       self.default_configuration_file,
                       default=self.default_configuration_file)

        # to parse subcommands
        self.subparsers = self.argparser.add_subparsers(
            title="COMMANDS",
            help="Available commands. Run `elasticluster cmd --help` "
            "to have information on command `cmd`.")

        for command in commands:
            if isinstance(command, AbstractCommand):
                command.setup(self.subparsers)

    def pre_run(self):
        cli.app.CommandLineApp.pre_run(self)
        if not os.path.isdir(self.params.storage):
            # We do not create *all* the parents, but we do create the
            # directory if we can.
            try:
                os.makedirs(self.params.storage)
            except OSError, ex:
                sys.stderr.write("Unable to create storage directory: "
                                 "%s\n" % (str(ex)))
                sys.exit(1)

        # If no configuration file was specified and default does not exists...
        if not os.path.isfile(self.params.config):
            if self.params.config == self.default_configuration_file:
            # Copy the default configuration file to the user's home
                if not os.path.exists(os.path.dirname(self.params.config)):
                    os.mkdir(os.path.dirname(self.params.config))
                template = os.path.join(
                    sys.prefix, 'share/elasticluster/etc/config.template.ini')
                log.warning("Deploying default configuration file to %s.",
                            self.params.config)
                shutil.copyfile(template, self.params.config)
            else:
                # Exit if supplied configuration file does not exists.
                if not os.path.isfile(self.params.config):
                    sys.stderr.write(
                        "Unable to read configuration file `%s`.\n" %
                        self.params.config)
                    sys.exit(1)

        if self.params.func:
            try:
                self.params.func.pre_run()
            except RuntimeError, ex:
                sys.stderr.write(str(ex).strip() + '\n')
                sys.exit(1)

    def main(self):
        """
        Elasticluster will start, stop, grow, shrink clusters on an EC2 cloud.
        """
        # This is the main entry point of the elasticluster.  First the
        # central configuration is created, which can be altered through
        # the command line interface. Then the given command from the
        # command line interface is called.

        # Set verbosity level
        loglevel = max(1, logging.WARNING - 10 * max(0, self.params.verbose))
        log.setLevel(loglevel)
        # initialize configuration singleton with given global parameters
        try:
            Configuration.Instance().file_path = self.params.config
            Configuration.Instance().storage_path = self.params.storage
        except Exception as ex:
            print "please specify a valid configuration file"
            sys.exit(1)

        # call the subcommand function (ususally execute)
        return self.params.func()


def main():
    app = ElasticCloud()
    app.run()


if __name__ == "__main__":
    main()
