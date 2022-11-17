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

from src.taipy.config import Config
from src.taipy.config._json_serializer import _JsonSerializer
from src.taipy.config.common.frequency import Frequency
from src.taipy.config.common.scope import Scope
from tests.config.utils.named_temporary_file import NamedTemporaryFile
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


def test_write_configuration_file():
    expected_config = (
        '{"TAIPY": {"root_folder": "./taipy/", "storage_folder": ".data/", '
        '"clean_entities_enabled": "True:bool", "repository_type": "filesystem"}, '
        '"unique_section_name": {"attribute": "my_attribute", "prop": "my_prop", "prop_int": "1:int", '
        '"prop_bool": "False:bool", "prop_list": ["p1"], "prop_scope": "SCENARIO:SCOPE", '
        '"prop_freq": "QUARTERLY:FREQUENCY"}, "section_name": {"default": '
        '{"attribute": "default_attribute", "prop": "default_prop", "prop_int": "0:int"}, '
        '"my_id": {"attribute": "my_attribute", "prop_int": "1:int", "prop_bool": "False:bool", '
        '"prop_list": ["unique_section_name:SECTION"], "prop_scope": "SCENARIO", "baz": "ENV[QUX]"}}}'
    )
    tf = NamedTemporaryFile()
    Config._serializer = _JsonSerializer()
    Config.configure_global_app(clean_entities_enabled=True)

    unique_section = Config.configure_unique_section_for_tests(
        attribute="my_attribute",
        prop="my_prop",
        prop_int=1,
        prop_bool=False,
        prop_list=[
            "p1",
        ],
        prop_scope=Scope.SCENARIO,
        prop_freq=Frequency.QUARTERLY,
    )
    Config.configure_section_for_tests(
        "my_id",
        "my_attribute",
        prop_int=1,
        prop_bool=False,
        prop_list=[unique_section],
        prop_scope="SCENARIO",
        baz="ENV[QUX]",
    )
    Config.export(tf.filename)
    actual_config = tf.read().strip()
    assert actual_config == "".join(expected_config.splitlines())


def test_read_configuration_file():
    config = (
        '{"TAIPY": {"root_folder": "./taipy/", "storage_folder": ".data/", '
        '"clean_entities_enabled": "True:bool", "repository_type": "filesystem"}, '
        '"unique_section_name": {"attribute": "my_attribute", "prop": "my_prop", "prop_int": "1:int", '
        '"prop_bool": "False:bool", "prop_list": ["p1"], "prop_scope": "SCENARIO:SCOPE", '
        '"prop_freq": "QUARTERLY:FREQUENCY"}, "section_name": {"default": '
        '{"attribute": "default_attribute", "prop": "default_prop", "prop_int": "0:int"}, '
        '"my_id": {"attribute": "my_attribute", "prop_int": "1:int", "prop_bool": "False:bool", '
        '"prop_list": ["unique_section_name"], "prop_scope": "SCENARIO"}}}'
    )
    Config._serializer = _JsonSerializer()
    tf = NamedTemporaryFile(config)

    Config.load(tf.filename)

    assert Config.unique_sections is not None
    assert Config.unique_sections[UniqueSectionForTest.name] is not None
    assert Config.unique_sections[UniqueSectionForTest.name].attribute == "my_attribute"
    assert Config.unique_sections[UniqueSectionForTest.name].prop == "my_prop"
    assert Config.unique_sections[UniqueSectionForTest.name].prop_int == 1
    assert Config.unique_sections[UniqueSectionForTest.name].prop_bool is False
    assert Config.unique_sections[UniqueSectionForTest.name].prop_list == [
        "p1",
    ]
    assert Config.unique_sections[UniqueSectionForTest.name].prop_scope == Scope.SCENARIO
    assert Config.unique_sections[UniqueSectionForTest.name].prop_freq == Frequency.QUARTERLY

    assert Config.sections is not None
    assert len(Config.sections) == 1
    assert Config.sections[SectionForTest.name] is not None
    assert len(Config.sections[SectionForTest.name]) == 2
    assert Config.sections[SectionForTest.name]["default"] is not None
    assert Config.sections[SectionForTest.name]["default"].attribute == "default_attribute"
    assert Config.sections[SectionForTest.name]["default"].prop == "default_prop"
    assert Config.sections[SectionForTest.name]["default"].prop_int == 0
    assert Config.sections[SectionForTest.name]["my_id"] is not None
    assert Config.sections[SectionForTest.name]["my_id"].attribute == "my_attribute"
    assert Config.sections[SectionForTest.name]["my_id"].prop is None
    assert Config.sections[SectionForTest.name]["my_id"].prop_int == 1
    assert Config.sections[SectionForTest.name]["my_id"].prop_bool is False
    assert Config.sections[SectionForTest.name]["my_id"].prop_list == ["unique_section_name"]

    tf2 = NamedTemporaryFile()
    Config.export(tf2.filename)
    actual_config_2 = tf2.read().strip()
    assert actual_config_2 == config
