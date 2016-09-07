#!/usr/bin/env python
# -*- coding: utf-8 -*-#
# @(#)setup.py
#
#
# Copyright (C) 2013, 2015, 2016 S3IT, University of Zurich. All rights reserved.
#
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import sys

# fix Python issue 15881 (on Python <2.7.5)
try:
    import multiprocessing
except ImportError:
    pass


# Ensure we use a recent enough version of setuptools: CentOS7 still ships with
# 0.9.8! There has been some instability in the support for PEP-496 environment
# markers recently, but Setuptools 20.10.0 seems to have restored full support
# for them, including `python_implementation`. See also issue #249.
from ez_setup import use_setuptools
use_setuptools(version='20.10.0')


## auxiliary functions
#
def read_whole_file(path):
    """
    Return file contents as a string.
    """
    with open(path, 'r') as stream:
        return stream.read()


## test runner setup
#
# See http://tox.readthedocs.org/en/latest/example/basic.html#integration-with-setuptools-distribute-test-commands
# on how to run tox when python setup.py test is run
#
from setuptools.command.test import test as TestCommand

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


## real setup description begins here
#
from setuptools import setup, find_packages

setup(
    name="elasticluster",
    version=read_whole_file("version.txt").strip(),
    description="A command line tool to create, manage and setup computing clusters hosted on a public or private cloud infrastructure.",
    long_description=read_whole_file('README.rst'),
    author="Services and Support for Science IT, University of Zurich",
    author_email="team@s3it.lists.uzh.ch",
    license="LGPL",
    keywords="cloud openstack amazon ec2 ssh hpc gridengine torque slurm batch job elastic",
    url="https://github.com/gc3-uzh-ch/elasticluster",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "License :: DFSG approved",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: Other",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Clustering",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Distributed Computing",
    ],
    packages=find_packages(),
    include_package_data=True,  # include files mentioned by MANIFEST.in
    entry_points={
        'console_scripts': [
            'elasticluster = elasticluster.main:main',
        ]
    },
    install_requires=[
        'PyCLI',
        'ansible>=2.0',
        'coloredlogs',
        'configobj',
        'paramiko',
        'voluptuous>=0.8.2',
        # EC2 clouds
        'boto',
        # GCE cloud
        'google-api-python-client',
        'python-gflags',
        # OpenStack clouds
        'netifaces',
        'python-novaclient;python_version>="2.7"',
        # Alternate dependencies for Python 2.6:
        # - pyCLI requires argparse,
        'argparse;python_version=="2.6"',
        # - OpenStack's "keystoneclient" requires `importlib`
        'importlib;python_version=="2.6"',
        # - support for Python 2.6 was removed from `novaclient` in commit
        #   81f8fa655ccecd409fe6dcda0d3763592c053e57 which is contained in
        #   releases 3.0.0 and above; however, we also need to pin down
        #   the version of `oslo.config` and all the dependencies thereof,
        #   otherwise `pip` will happily download the latest and
        #   incompatible version,since `python-novaclient` specifies only
        #   the *minimal* version of dependencies it is compatible with...
        'stevedore<1.10.0;python_version=="2.6"',
        'debtcollector<1.0.0;python_version=="2.6"',
        'keystoneauth<2.0.0;python_version=="2.6"',
        # yes, there"s `keystoneauth` and `keystoneauth1` !!
        'keystoneauth1<2.0.0;python_version=="2.6"',
        'oslo.config<3.0.0;python_version=="2.6"',
        'oslo.i18n<3.1.0;python_version=="2.6"',
        'oslo.serialization<2.1.0;python_version=="2.6"',
        'oslo.utils<3.1.0;python_version=="2.6"',
        'python-novaclient<3.0.0;python_version=="2.6"',
    ],
    tests_require=['tox', 'mock', 'pytest'],  # read right-to-left
    cmdclass={'test': Tox},
)
