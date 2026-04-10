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

import logging
import sys


def _logger(name=None):
    if not name:
        name = __name__.split('.')[0]
    __logger = logging.getLogger(name)

    if not __logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(
            logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                '%Y-%m-%d %H:%M:%S'
            )
        )

        __logger.setLevel(logging.INFO)
        __logger.addHandler(handler)

    return __logger


logger = _logger()
