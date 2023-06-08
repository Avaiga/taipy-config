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

import pytest

from src.taipy.config._config import _Config
from src.taipy.config._config_comparator._config_comparator import _ConfigComparator
from src.taipy.config._serializer._toml_serializer import _TomlSerializer
from src.taipy.config.checker.issue_collector import IssueCollector
from src.taipy.config.config import Config
from src.taipy.config.section import Section
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


@pytest.fixture(scope="function", autouse=True)
def reset():
    reset_configuration_singleton()
    register_test_sections()


def reset_configuration_singleton():
    Config.unblock_update()
    Config._default_config = _Config()._default_config()
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_file_config = _Config()
    Config._applied_config = _Config()
    Config._collector = IssueCollector()
    Config._serializer = _TomlSerializer()
    Config._comparator = _ConfigComparator()


def register_test_sections():
    Config._register_default(UniqueSectionForTest("default_attribute"))
    Config.configure_unique_section_for_tests = UniqueSectionForTest._configure
    Config.unique_section_name = Config.unique_sections[UniqueSectionForTest.name]

    Config._register_default(SectionForTest(Section._DEFAULT_KEY, "default_attribute", prop="default_prop", prop_int=0))
    Config.configure_section_for_tests = SectionForTest._configure
    Config.section_name = Config.sections[SectionForTest.name]
