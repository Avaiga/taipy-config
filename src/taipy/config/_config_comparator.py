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
import re
from typing import Dict, List, Union

from deepdiff import DeepDiff

from ..logger._taipy_logger import _TaipyLogger
from ._base_serializer import _BaseSerializer
from ._config import _Config
from .config import Config


class _ConfigComparator(dict):
    """Compare between 2 _Config object to check for compatibility.

    Return a dictionary with the following format:
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

    _ADDED_ITEMS_KEY = "added_items"
    _REMOVED_ITEMS_KEY = "removed_items"
    _MODIFIED_ITEMS_KEY = "modified_items"

    _BLOCKED_SECTION_KEY = "blocked_diff_sections"
    _UNBLOCKED_SECTION_KEY = "unblocked_diff_sections"

    _UNBLOCKED_SECTIONS = set()

    def __init__(self, old_conf: _Config, new_conf: _Config):
        super().__init__()

        self.old_conf_json = json.loads(Config._to_json(old_conf))  # type: ignore
        self.new_conf_json = json.loads(Config._to_json(new_conf))  # type: ignore

        self.deepdiff_result = DeepDiff(self.old_conf_json, self.new_conf_json)

        self.__check_added_items()
        self.__check_removed_items()
        self.__check_modified_items()

        self.__sort_by_section()
        self.__logger = _TaipyLogger._get_logger()

    def __sort_by_section(self):
        if self.get(self._BLOCKED_SECTION_KEY):
            for key in self[self._BLOCKED_SECTION_KEY].keys():
                self[self._BLOCKED_SECTION_KEY][key].sort(key=lambda x: x[0][0])

        if self.get(self._UNBLOCKED_SECTION_KEY):
            for key in self[self._UNBLOCKED_SECTION_KEY].keys():
                self[self._UNBLOCKED_SECTION_KEY][key].sort(key=lambda x: x[0][0])

    def __check_added_items(self):
        if dictionary_item_added := self.deepdiff_result.get("dictionary_item_added"):
            for item_added in dictionary_item_added:
                section_name, config_id, attribute = self.__get_changed_entity_attribute(item_added)
                diff_sections = self.__get_section(section_name)

                if attribute:
                    value_added = self.new_conf_json[section_name][config_id][attribute]
                else:
                    value_added = self.new_conf_json[section_name][config_id]

                section_name = self.__rename_global_node_name(section_name)
                self.__create_or_append_list(
                    diff_sections,
                    self._ADDED_ITEMS_KEY,
                    ((section_name, config_id, attribute), (value_added)),
                )

    def __check_removed_items(self):
        if dictionary_item_removed := self.deepdiff_result.get("dictionary_item_removed"):
            for item_removed in dictionary_item_removed:
                section_name, config_id, attribute = self.__get_changed_entity_attribute(item_removed)
                diff_sections = self.__get_section(section_name)

                if attribute:
                    value_removed = self.old_conf_json[section_name][config_id][attribute]
                else:
                    value_removed = self.old_conf_json[section_name][config_id]

                section_name = self.__rename_global_node_name(section_name)
                self.__create_or_append_list(
                    diff_sections,
                    self._REMOVED_ITEMS_KEY,
                    ((section_name, config_id, attribute), (value_removed)),
                )

    def __check_modified_items(self):
        if values_changed := self.deepdiff_result.get("values_changed"):
            for item_changed, value_changed in values_changed.items():
                section_name, config_id, attribute = self.__get_changed_entity_attribute(item_changed)
                diff_sections = self.__get_section(section_name)

                section_name = self.__rename_global_node_name(section_name)
                self.__create_or_append_list(
                    diff_sections,
                    self._MODIFIED_ITEMS_KEY,
                    ((section_name, config_id, attribute), (value_changed["old_value"], value_changed["new_value"])),
                )

        # Iterable item added will be considered a modified item
        if iterable_item_added := self.deepdiff_result.get("iterable_item_added"):
            self.__check_modified_iterable(iterable_item_added)

        # Iterable item removed will be considered a modified item
        if iterable_item_removed := self.deepdiff_result.get("iterable_item_removed"):
            self.__check_modified_iterable(iterable_item_removed)

    def __check_modified_iterable(self, iterable_items):
        for item in iterable_items:
            section_name, config_id, attribute = self.__get_changed_entity_attribute(item)
            diff_sections = self.__get_section(section_name)

            if attribute:
                new_value = self.new_conf_json[section_name][config_id][attribute]
                old_value = self.old_conf_json[section_name][config_id][attribute]
            else:
                new_value = self.new_conf_json[section_name][config_id]
                old_value = self.old_conf_json[section_name][config_id]

            section_name = self.__rename_global_node_name(section_name)
            modified_value = ((section_name, config_id, attribute), (old_value, new_value))

            if modified_value not in diff_sections[self._MODIFIED_ITEMS_KEY]:
                self.__create_or_append_list(
                    diff_sections,
                    self._MODIFIED_ITEMS_KEY,
                    modified_value,
                )

    def __get_section(self, section_name: str) -> Dict[str, List]:
        if section_name in self._UNBLOCKED_SECTIONS:
            if not self.get(self._UNBLOCKED_SECTION_KEY):
                self[self._UNBLOCKED_SECTION_KEY] = {}
            return self[self._UNBLOCKED_SECTION_KEY]

        if not self.get(self._BLOCKED_SECTION_KEY):
            self[self._BLOCKED_SECTION_KEY] = {}
        return self[self._BLOCKED_SECTION_KEY]

    def __create_or_append_list(self, diff_dict, key, value):
        if diff_dict.get(key):
            diff_dict[key].append(value)
        else:
            diff_dict[key] = [value]

    def __get_changed_entity_attribute(self, attribute_bracket_notation):
        """Split the entity name, entity id (if exists), and the attribute name from JSON bracket notation."""
        try:
            section_name, config_id, attribute = re.findall(r"\[\'(.*?)\'\]", attribute_bracket_notation)
        except ValueError:
            section_name, config_id = re.findall(r"\[\'(.*?)\'\]", attribute_bracket_notation)
            attribute = None

        return section_name, config_id, attribute

    def __rename_global_node_name(self, node_name):
        if node_name == _BaseSerializer._GLOBAL_NODE_NAME:
            return "Global Configuration"
        return node_name

    def _log_blocked_sections(self):
        if blocked_sections := self.get(self._BLOCKED_SECTION_KEY):
            self.__log_message(blocked_sections, self.__logger.error)

    def _log_unblocked_sections(self):
        if unblocked_sections := self.get(self._UNBLOCKED_SECTION_KEY):
            self.__log_message(unblocked_sections, self.__logger.info)

    def __log_message(self, diff_sections, log_fct):
        dq = '"'

        if added_items := diff_sections.get(self._ADDED_ITEMS_KEY):
            for diff in added_items:
                ((section_name, config_id, attribute), added_object) = diff
                log_fct(
                    f"{section_name} {dq}{config_id}{dq} "
                    f"{f'has attribute {dq}{attribute}{dq}' if attribute else 'was'} added: {added_object}"
                )

        if removed_items := diff_sections.get(self._REMOVED_ITEMS_KEY):
            for diff in removed_items:
                ((section_name, config_id, attribute), removed_object) = diff
                log_fct(
                    f"{section_name} {dq}{config_id}{dq} "
                    f"{f'has attribute {dq}{attribute}{dq}' if attribute else 'was'} removed"
                )

        if modified_items := diff_sections.get(self._MODIFIED_ITEMS_KEY):
            for diff in modified_items:
                ((section_name, config_id, attribute), (old_value, new_value)) = diff
                log_fct(
                    f"{section_name} {dq}{config_id}{dq} "
                    f"{f'has attribute {dq}{attribute}{dq}' if attribute else 'was'} modified: "
                    f"{old_value} -> {new_value}"
                )

    @classmethod
    def _unblock_section(cls, section_name: Union[str, List[str]]):
        if isinstance(section_name, str):
            section_name = [section_name]

        cls._UNBLOCKED_SECTIONS.update(section_name)
