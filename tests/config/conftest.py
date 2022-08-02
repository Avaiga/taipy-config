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

import pytest

from src.taipy.config import Config, Section, IssueCollector
from src.taipy.config._config import _Config
from src.taipy.config._toml_serializer import _TomlSerializer
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


@pytest.fixture(scope="function", autouse=True)
def reset():
    reset_configuration_singleton()


def reset_configuration_singleton():
    Config._default_config = _Config()._default_config()
    Config._python_config = _Config()
    Config._file_config = None
    Config._env_file_config = None
    Config._applied_config = _Config._default_config()
    Config._collector = IssueCollector()
    Config._serializer = _TomlSerializer()
    Config._register_default(UniqueSectionForTest("default_attribute"))
    Config.configure_unique_section_for_tests = UniqueSectionForTest._configure
    Config._register_default(SectionForTest(Section._DEFAULT_KEY, "default_attribute",
                                            prop="default_prop",
                                            prop_int="0:int"))
    Config.configure_section_for_tests = SectionForTest._configure
