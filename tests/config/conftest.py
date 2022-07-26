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

from src.taipy.config import Config, Section
from src.taipy.config._config import _Config
from tests.config.section_for_test import SectionForTest
from tests.config.unique_section_for_test import UniqueSectionForTest


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    Config._default_config = _Config()._default_config()
    Config._python_config = _Config()
    Config._file_config = None
    Config._env_file_config = None
    Config._applied_config = _Config._default_config()
    Config._register_default(UniqueSectionForTest("default_attribute"))
    Config.configure_unique_section_for_test = UniqueSectionForTest._configure
    Config._register_default(SectionForTest(Section._DEFAULT_KEY, "default_attribute"))
    Config.configure_section_for_test = SectionForTest._configure
