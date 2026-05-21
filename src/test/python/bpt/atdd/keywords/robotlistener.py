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

import base64
import logging
import os

from robot.api import logger


class RobotListener:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(
            self,
            logger_name='RobotFramework'
    ):
        self.ui_driver_logger = logging.getLogger(
            logger_name
        )

        self.log_level = self.ui_driver_logger.level

        self.ui_driver = None
        self.no_image_file = True
        self.failed_case_only = True
        self.images_home = os.path.join(
            os.path.dirname(os.path.curdir),
            'screenshots'
        )
        self.image_size = (900, 600)

    def enable_screenshot(
            self,
            ui_driver,
            embedded_image_only=True,
            failed_case_only=True,
            screenshots_home=None,
            image_size=None
    ):
        self.ui_driver = ui_driver
        self.no_image_file = embedded_image_only
        self.failed_case_only = failed_case_only
        if screenshots_home:
            self.images_home = screenshots_home

        if image_size:
            self.image_size = image_size

    def disable_screenshot(self):
        if self.ui_driver:
            del self.ui_driver
            self.ui_driver = None

    def _start_suite(self, name, attributes):
        self.ui_driver_logger.setLevel(
            logging.WARNING
        )

        logger.info(
            'Test execution on suite {}({}) started at {}'.format(
                name,
                attributes.get('id'),
                attributes.get('starttime')
            ),
            also_console=True
        )

    def _log_message(self, message):
        msg = message.get('message')
        html = message.get('html') == 'yes'
        png = None

        try:
            png = self.ui_driver.take_screenshot()

            if self.no_image_file and html:
                encoded_base64 = base64.b64encode(png)

                logger.info(
                    '<img alt="{}" width="{}" height="{}" '
                    'src="data:image/png;base64,{}" />'.format(
                        msg,
                        *self.image_size,
                        b''.join(
                            encoded_base64[index * 40:(index + 1) * 40]
                            for index in range(
                                int((len(encoded_base64) / 40)) + 1
                            )
                        ).decode('ascii')
                    ), html=True
                )
        except Exception:
            pass  # Ignore exceptions while taking screenshots
        finally:
            if png:
                del png

    def _close(self):
        self.ui_driver_logger.setLevel(
            self.log_level
        )
