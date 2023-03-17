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

from src.taipy.config import IssueCollector
from src.taipy.config.checker._checkers._config_checker import _ConfigChecker


class CheckerForTest(_ConfigChecker):
    def _check(self) -> IssueCollector:
        self._info("info_field", "info_value", "info_message")
        self._warning("warning_field", "warning_value", "warning_message")
        self._error("error_field", "error_value", "error_message")
        return self._collector
