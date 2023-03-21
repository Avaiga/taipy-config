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

from typing import Any, List

from ...logger._taipy_logger import _TaipyLogger
from .issue import Issue


class IssueCollector:
    """
    A collection of issues (instances of class `Issue^`).

    Attributes:
        errors (List[Issue^]): List of ERROR issues collected.
        warnings (List[Issue^]): List WARNING issues collected.
        infos (List[Issue^]): List INFO issues collected.
        all (List[Issue^]): List of all issues collected ordered by decreasing level (ERROR, WARNING and INFO).
    """

    _ERROR_LEVEL = "ERROR"
    _WARNING_LEVEL = "WARNING"
    _INFO_LEVEL = "INFO"

    def __init__(self):
        self._errors: List[Issue] = []
        self._warnings: List[Issue] = []
        self._infos: List[Issue] = []
        self.__logger = _TaipyLogger._get_logger()

    @property
    def all(self) -> List[Issue]:
        return self._errors + self._warnings + self._infos

    @property
    def infos(self) -> List[Issue]:
        return self._infos

    @property
    def warnings(self) -> List[Issue]:
        return self._warnings

    @property
    def errors(self) -> List[Issue]:
        return self._errors

    def _add_error(self, field: str, value: Any, message: str, checker_name: str):
        issue = Issue(self._ERROR_LEVEL, field, value, message, checker_name)
        self._errors.append(issue)
        self.__logger.error(str(issue))

    def _add_warning(self, field: str, value: Any, message: str, checker_name: str):
        issue = Issue(self._WARNING_LEVEL, field, value, message, checker_name)
        self._warnings.append(issue)
        self.__logger.warning(str(issue))

    def _add_info(self, field: str, value: Any, message: str, checker_name: str):
        issue = Issue(self._INFO_LEVEL, field, value, message, checker_name)
        self._infos.append(issue)
        self.__logger.info(str(issue))
