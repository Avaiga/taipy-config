# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import functools

from ..exceptions.exceptions import ConfigurationUpdateBlocked


class _ConfigBlocker:
    """Configuration blocker singleton."""

    __block_config_update = False

    @classmethod
    def _block(cls):
        cls.__block_config_update = True

    @classmethod
    def _unblock(cls):
        cls.__block_config_update = False

    @classmethod
    def _check(cls):
        def inner(f):
            @functools.wraps(f)
            def _check_if_is_blocking(*args, **kwargs):
                if cls.__block_config_update:
                    raise ConfigurationUpdateBlocked()

                return f(*args, **kwargs)

            return _check_if_is_blocking

        return inner
