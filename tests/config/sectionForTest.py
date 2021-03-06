# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from copy import copy
from typing import Dict, Any

from src.taipy.config import Section, Config


class SectionForTest(Section):

    name = "sub"
    _MY_ATTRIBUTE_KEY = "attribute"

    def __init__(self, attribute: str = None, **properties):
        self._attribute = attribute
        super().__init__(**properties)

    def __copy__(self):
        return SectionForTest(self._attribute, **copy(self._properties))

    @property
    def attribute(self):
        return self._replace_templates(self._attribute)

    @attribute.setter  # type: ignore
    def attribute(self, val):
        self._attribute = val

    def _to_dict(self):
        as_dict = {}
        if self._attribute is not None:
            as_dict[self._MY_ATTRIBUTE_KEY] = self._attribute
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, as_dict: Dict[str, Any]):
        config = SectionForTest()
        config._attribute = as_dict.pop(cls._MY_ATTRIBUTE_KEY, None)
        config._properties = as_dict
        return config

    def _update(self, as_dict: Dict[str, Any]):
        self._attribute = as_dict.pop(self._MY_ATTRIBUTE_KEY, self._attribute)
        self._properties.update(as_dict)

    @staticmethod
    def _configure(attribute: str, **properties):
        section = SectionForTest(attribute, **properties)
        Config._register(section)
        return Config.sections[SectionForTest.name]


Config._register_default(SectionForTest("default_attribute"))
Config.configure_section_for_test = SectionForTest._configure

