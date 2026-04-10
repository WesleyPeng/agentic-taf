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

import yaml

from taf.foundation.utils.traits import Serializable


class YAMLData(yaml.YAMLObject, Serializable):
    yaml_tag = '!YAMLData'

    def __init__(self, **kwargs):
        super(YAMLData, self).__init__()

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
    def load(cls, path):
        try:
            with open(path, 'r') as stream:
                data = yaml.load(stream)
        except IOError as ioe:
            data = dict(
                errno=ioe.errno,
                filename=ioe.filename,
                # message=ioe.message,
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
