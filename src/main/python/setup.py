# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Wesley Peng
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from os.path import abspath, dirname, isdir, isfile, join


def find_packages(where='.', exclude=()):
    def is_package(path):
        return isdir(path) and isfile(
            join(path, '__init__.py')
        )

    packages = []
    for root, dirs, files in os.walk(where):
        for dir_name in dirs:
            pkg_path = join(root, dir_name)
            package = '.'.join(pkg_path.split(os.sep)[1:])

            if package not in exclude and (
                    is_package(pkg_path)
            ):
                packages.append(package)

    return packages


try:
    from setuptools import setup, find_packages  # noqa: F811
except ImportError:
    from distutils.core import setup

LONG_DESC = """
Agentic Test Automation Framework
"""

CURDIR = dirname(abspath(__file__))

with open(
        join(CURDIR, 'requirements.txt')
) as file_requires:
    REQUIREMENTS = file_requires.read().splitlines()

PACKAGES = find_packages(
    exclude=(
        'ut',
    )
)

setup(
    name='Agentic-TAF',
    version='1.0.0',
    description='Agentic Test Automation Framework',
    long_description=LONG_DESC,
    install_requires=REQUIREMENTS,
    packages=PACKAGES,
    # test_suite='ut'
)
