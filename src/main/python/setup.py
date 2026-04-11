# Copyright (c) 2017-2026 Wesley Peng
#
# Licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0).
# You may obtain a copy of the License at
#
# https://www.gnu.org/licenses/lgpl-3.0.html
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

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
