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

import yaml

from taf.foundation.utils.traits import Serializable


class YAMLData(yaml.YAMLObject, Serializable):
    yaml_tag = '!YAMLData'

    def __init__(self, **kwargs):
        super().__init__()

        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def __getattr__(self, item):
        return self.__getattribute__(item)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __setattr__(self, name, value):
        assert (name is not None) and getattr(
            name, 'strip', lambda: None
        )()

        vars(self).update(
            **{
                name: self.normalize_data(value)
            }
        )

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __iadd__(self, other):
        _data = self.normalize_data(other)

        if not isinstance(_data, type(self)):
            raise ValueError(
                'Assigning invalid value: ({})'.format(
                    other
                )
            )

        for key, value in vars(_data).items():
            vars(self).update(
                **{
                    key: value
                }
            )

        return self

    def dump(self, path):
        try:
            for key, value in vars(self).copy().items():
                if hasattr(value, '__dict__') and (
                        not isinstance(
                            value, yaml.YAMLObject
                        )
                ):
                    self.__delattr__(key)

            with open(path, 'w') as stream:
                yaml.dump(self, stream)
        except Exception:
            raise

    @classmethod
    def load(cls, path: str) -> 'YAMLData':
        try:
            with open(path, 'r') as stream:
                data = yaml.full_load(stream)
        except IOError as ioe:
            data = dict(
                errno=ioe.errno,
                filename=ioe.filename,
                strerror=ioe.strerror
            )
        except Exception:
            raise

        return cls.normalize_data(data)

    @classmethod
    def normalize_data(cls, data):
        if not isinstance(data, YAMLData):
            if hasattr(data, '__dict__'):
                data = YAMLData(**vars(data))
            elif isinstance(data, dict):
                data = YAMLData(**data)
            elif isinstance(data, (list, tuple)):
                data = [
                    cls.normalize_data(datum)
                    for datum in data
                ]
            else:
                data = yaml.safe_load(
                    yaml.safe_dump(data)
                )

        return data
