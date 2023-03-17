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

from typing import List, Type

from .._config import _Config
from ._checkers._config_checker import _ConfigChecker
from ._checkers._gLobal_config_checker import _GlobalConfigChecker
from .issue_collector import IssueCollector


class _Checker:
    """Holds the various checkers to perform on the config."""

    _checkers: List[Type[_ConfigChecker]] = [_GlobalConfigChecker]  # type: ignore

    @classmethod
    def _check_all(cls, _config: _Config):
        collector = IssueCollector()
        for checker in cls._checkers:
            checker(_config, collector)._check()
        return collector

    @classmethod
    def _check(cls, _config: _Config, checker: Type[_ConfigChecker]):
        collector = IssueCollector()
        checker(_config, collector)._check()
        return collector

    @classmethod
    def add_checker(cls, checker_class: Type[_ConfigChecker]):
        cls._checkers.append(checker_class)
