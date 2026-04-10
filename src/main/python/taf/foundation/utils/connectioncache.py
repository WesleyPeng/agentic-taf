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

import uuid
from collections import OrderedDict


class ConnectionCache(object):
    conns = OrderedDict()
    current_key = None
    closed = set()

    def __init__(self, identifier=None):
        ConnectionCache.current_key = self._normalize_id(
            identifier
        )

    @classmethod
    def register(cls, conn, identifier=None):
        if not conn:
            raise ValueError('Invalid Connection')

        key = cls._normalize_id(identifier)
        if key in cls.conns:
            cls._unregister(key)

        cls.conns[key] = conn
        cls.current_key = key

        return cls.current_key

    @property
    def current(self):
        return self.conns.get(
            self.current_key
        )

    def get_connection(self, key):
        return self.conns.get(key)

    def switch(self, key):
        if key not in self.conns:
            raise ValueError(
                'Unknown key:{}'.format(key)
            )
        else:
            ConnectionCache.current_key = key

        return self.conns.get(key)

    def close(self, key=None):
        try:
            self._unregister(
                self._normalize_id(key)
            )
        except Exception:
            raise
        finally:
            if self.conns:
                if key == self.current_key:
                    ConnectionCache.current_key = \
                        list(self.conns.keys())[-1]
            else:
                ConnectionCache.current_key = None

    def close_all(self):
        for key in self.conns:
            self.close(key)

        ConnectionCache.closed.clear()

    @classmethod
    def _unregister(cls, key):
        _conn = cls.conns.get(key, None)

        if _conn:
            try:
                if hasattr(_conn, 'quit'):
                    _conn.quit()

                cls.closed.add(_conn)
            finally:
                cls._dispose(key)

    @classmethod
    def _normalize_id(cls, identifier=None):
        if not identifier:
            identifier = cls.current_key

        if not (identifier and str(identifier).strip()):
            identifier = uuid.uuid4()

        return identifier

    @classmethod
    def _dispose(cls, key):
        if key in cls.conns:
            cls.conns[key] = None
            del cls.conns[key]
