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

import json
from copy import copy
from typing import Optional, Set, Union

from deepdiff import DeepDiff

from ...logger._taipy_logger import _TaipyLogger
from .._config import _Config
from .._serializer._json_serializer import _JsonSerializer
from ..exceptions.exceptions import ConflictedConfigurationError
from ._comparator_result import _ComparatorResult


class _ConfigComparator:

    _UNCONFLICTED_SECTIONS: Set[str] = set()

    __logger = _TaipyLogger._get_logger()

    @classmethod
    def _add_unconflicted_section(cls, section_name: Union[str, Set[str]]):
        if isinstance(section_name, str):
            section_name = {section_name}

        cls._UNCONFLICTED_SECTIONS.update(section_name)

    @classmethod
    def _compare(
        cls,
        old_config: _Config,
        new_config: _Config,
        old_version_number: Optional[str] = None,
        new_version_number: Optional[str] = None,
        raise_error: bool = True,
    ):
        """Compare between 2 _Config object to check for compatibility.

        Args:
            old_config (_Config): The old _Config.
            new_config (_Config): The new _Config.
            old_version_number (str, optional): The old version number for logging. Defaults to None.
            new_version_number (str, optional): The new version number for logging. Defaults to None.
            raise_error (bool, optional): Raise exception if there is error or not. Defaults to True.

        Raises:
            ConflictedConfigurationError: Raise if there is conflicted between the 2 _Config and raise_error is True.

        Returns:
            _ComparatorResult: Return a _ComparatorResult dictionary with the following format:
        ```python
        {
            "added_items": [
                ((section_name_1, config_id_1, attribute_1), added_object_1),
                ((section_name_2, config_id_2, attribute_2), added_object_2),
            ],
            "removed_items": [
                ((section_name_1, config_id_1, attribute_1), removed_object_1),
                ((section_name_2, config_id_2, attribute_2), removed_object_2),
            ],
            "modified_items": [
                ((section_name_1, config_id_1, attribute_1), (old_value_1, new_value_1)),
                ((section_name_2, config_id_2, attribute_2), (old_value_2, new_value_2)),
            ],
        }
        ```
        """
        old_json_config = json.loads(_JsonSerializer._serialize(old_config))
        new_json_config = json.loads(_JsonSerializer._serialize(new_config))

        config_deepdiff = DeepDiff(old_json_config, new_json_config)

        comparator_result = _ComparatorResult(copy(cls._UNCONFLICTED_SECTIONS))

        comparator_result._check_added_items(config_deepdiff, new_json_config)
        comparator_result._check_removed_items(config_deepdiff, old_json_config)
        comparator_result._check_modified_items(config_deepdiff, old_json_config, new_json_config)
        comparator_result._sort_by_section()

        cls.__log_message(comparator_result, old_version_number, new_version_number)

        if raise_error:
            if comparator_result.get(_ComparatorResult.CONFLICTED_SECTION_KEY):
                raise ConflictedConfigurationError

        return comparator_result

    @classmethod
    def __log_message(
        cls,
        comparator_result: _ComparatorResult,
        old_version_number: Optional[str] = None,
        new_version_number: Optional[str] = None,
    ):
        old_config_str = (
            f"version {old_version_number} Configuration" if old_version_number else "current Configuration"
        )
        new_config_str = (
            f"version {new_version_number} Configuration" if new_version_number else "current Configuration"
        )

        if unconflicted_sections := comparator_result.get(_ComparatorResult.UNCONFLICTED_SECTION_KEY):
            unconflicted_messages = cls.__get_messages(unconflicted_sections)
            cls.__logger.info(
                f"There are non-conflicting changes between the {old_config_str}"
                f" and the {new_config_str}:\n\t" + "\n\t".join(unconflicted_messages)
            )

        if conflicted_sections := comparator_result.get(_ComparatorResult.CONFLICTED_SECTION_KEY):
            conflicted_messages = cls.__get_messages(conflicted_sections)
            cls.__logger.error(
                f"The {old_config_str} is conflicted with the {new_config_str}:\n\t" + "\n\t".join(conflicted_messages)
            )
            cls.__logger.error("To override these changes, run your application with --force option.")

    @classmethod
    def __get_messages(cls, diff_sections):
        dq = '"'
        messages = []

        if added_items := diff_sections.get(_ComparatorResult.ADDED_ITEMS_KEY):
            for diff in added_items:
                ((section_name, config_id, attribute), added_object) = diff
                messages.append(
                    f"{section_name} {dq}{config_id}{dq} "
                    f"{f'has attribute {dq}{attribute}{dq}' if attribute else 'was'} added: {added_object}"
                )

        if removed_items := diff_sections.get(_ComparatorResult.REMOVED_ITEMS_KEY):
            for diff in removed_items:
                ((section_name, config_id, attribute), removed_object) = diff
                messages.append(
                    f"{section_name} {dq}{config_id}{dq} "
                    f"{f'has attribute {dq}{attribute}{dq}' if attribute else 'was'} removed"
                )

        if modified_items := diff_sections.get(_ComparatorResult.MODIFIED_ITEMS_KEY):
            for diff in modified_items:
                ((section_name, config_id, attribute), (old_value, new_value)) = diff
                messages.append(
                    f"{section_name} {dq}{config_id}{dq} "
                    f"{f'has attribute {dq}{attribute}{dq}' if attribute else 'was'} modified: "
                    f"{old_value} -> {new_value}"
                )

        return messages
