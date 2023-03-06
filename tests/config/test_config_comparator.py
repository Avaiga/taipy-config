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

from src.taipy.config._config import _Config
from src.taipy.config._config_comparator import _ConfigComparator
from src.taipy.config.global_app.global_app_config import GlobalAppConfig
from tests.config.utils.section_for_tests import SectionForTest
from tests.config.utils.unique_section_for_tests import UniqueSectionForTest


def test_config_comparator_return():
    unique_section_1 = UniqueSectionForTest(attribute="unique_attribute_1", prop="unique_prop_1")
    section_1 = SectionForTest("section_1", attribute="attribute_1", prop="prop_1")
    section_2a = SectionForTest("section_2", attribute=2, prop="prop_2")
    section_2b = SectionForTest("section_2", attribute=20, prop="prop_2b")
    section_3 = SectionForTest("section_3", attribute=3, prop="prop_3")
    section_4 = SectionForTest("section_4", attribute=4, prop="prop_4")
    section_5a = SectionForTest("section_5", attribute=[1, 2, 3, 4, 5], prop=["prop_5"])
    section_5b = SectionForTest("section_5", attribute=[1, 2], prop=["prop_4", "prop_5"])

    _config_1 = _Config._default_config()
    _config_1._sections[SectionForTest.name] = {
        "section_1": section_1,
        "section_2": section_2a,
        "section_3": section_3,
        "section_5": section_5a,
    }
    _config_1._unique_sections[UniqueSectionForTest.name] = unique_section_1

    config_diff = _ConfigComparator(_config_1, _config_1)
    assert config_diff == {}

    _config_2 = _Config._default_config()
    # Update global config
    _config_2._global_config = GlobalAppConfig(
        root_folder="foo",
        storage_folder="bar",
        repository_properties={"foo": "bar"},
        repository_type="baz",
        clean_entities_enabled=True,
    )
    # Update section_2 and section_5, remove section_3, and add section 4
    _config_2._sections[SectionForTest.name] = {
        "section_1": section_1,
        "section_2": section_2b,
        "section_4": section_4,
        "section_5": section_5b,
    }
    _config_2._unique_sections[UniqueSectionForTest.name] = unique_section_1

    config_diff = _ConfigComparator(_config_1, _config_2)
    assert config_diff.get("unblocked_diff_sections") is None
    blocked_config_diff = config_diff["blocked_diff_sections"]

    # The result was sorted so test by indexing is fine.
    assert len(blocked_config_diff["added_items"]) == 2
    assert blocked_config_diff["added_items"][1] == (
        ("section_name", "section_4", None),
        {"attribute": "4:int", "prop": "prop_4"},
    )
    assert blocked_config_diff["added_items"][0] == (
        ("Global Configuration", "repository_properties", None),
        {"foo": "bar"},
    )

    assert len(blocked_config_diff["modified_items"]) == 8
    assert blocked_config_diff["modified_items"][0] == (
        ("Global Configuration", "root_folder", None),
        ("./taipy/", "foo"),
    )
    assert blocked_config_diff["modified_items"][1] == (
        ("Global Configuration", "storage_folder", None),
        (".data/", "bar"),
    )
    assert blocked_config_diff["modified_items"][2] == (
        ("Global Configuration", "clean_entities_enabled", None),
        ("ENV[TAIPY_CLEAN_ENTITIES_ENABLED]", "True:bool"),
    )
    assert blocked_config_diff["modified_items"][3] == (
        ("Global Configuration", "repository_type", None),
        ("filesystem", "baz"),
    )
    assert blocked_config_diff["modified_items"][4] == (("section_name", "section_2", "attribute"), ("2:int", "20:int"))
    assert blocked_config_diff["modified_items"][5] == (("section_name", "section_2", "prop"), ("prop_2", "prop_2b"))
    assert blocked_config_diff["modified_items"][6] == (
        ("section_name", "section_5", "prop"),
        (["prop_5"], ["prop_4", "prop_5"]),
    )
    assert blocked_config_diff["modified_items"][7] == (
        ("section_name", "section_5", "attribute"),
        (["1:int", "2:int", "3:int", "4:int", "5:int"], ["1:int", "2:int"]),
    )

    assert len(blocked_config_diff["removed_items"]) == 1
    assert blocked_config_diff["removed_items"][0] == (
        ("section_name", "section_3", None),
        {"attribute": "3:int", "prop": "prop_3"},
    )


def test_unblock_section_when_compare(caplog):
    unique_section_1 = UniqueSectionForTest(attribute="unique_attribute_1", prop="unique_prop_1")
    section_1 = SectionForTest("section_1", attribute="attribute_1", prop="prop_1")
    section_2 = SectionForTest("section_2", attribute=2, prop="prop_2")

    _config_1 = _Config._default_config()
    _config_1._sections[SectionForTest.name] = {"section_1": section_1}
    _config_1._unique_sections[UniqueSectionForTest.name] = unique_section_1

    _config_2 = _Config._default_config()
    _config_2._global_config = GlobalAppConfig.default_config()
    _config_2._global_config.repository_properties = {"foo": "bar"}
    _config_2._sections[SectionForTest.name] = {"section_1": section_2}
    _config_2._unique_sections[UniqueSectionForTest.name] = unique_section_1

    # Compare 2 Configuration
    config_diff = _ConfigComparator(_config_1, _config_2)

    config_diff._log_unblocked_sections()
    assert caplog.text == ""
    assert config_diff.get("unblocked_diff_sections") is None
    caplog.clear()

    blocked_config_diff = config_diff["blocked_diff_sections"]
    config_diff._log_blocked_sections()
    assert len(caplog.text.strip().split("\n")) == 3
    assert len(blocked_config_diff["added_items"]) == 1
    assert len(blocked_config_diff["modified_items"]) == 2
    assert blocked_config_diff.get("removed_items") is None
    caplog.clear()

    # Ignore any diff of "section_name" and compare
    _ConfigComparator._unblock_section("section_name")
    config_diff = _ConfigComparator(_config_1, _config_2)

    config_diff._log_blocked_sections()
    blocked_config_diff = config_diff["blocked_diff_sections"]
    assert len(caplog.text.strip().split("\n")) == 1
    assert len(blocked_config_diff["added_items"]) == 1
    assert blocked_config_diff.get("modified_items") is None
    assert blocked_config_diff.get("removed_items") is None
    caplog.clear()

    config_diff._log_unblocked_sections()
    unblocked_config_diff = config_diff["unblocked_diff_sections"]
    assert len(caplog.text.strip().split("\n")) == 2
    assert unblocked_config_diff.get("added_items") is None
    assert len(unblocked_config_diff["modified_items"]) == 2
    assert unblocked_config_diff.get("removed_items") is None
    caplog.clear()

    # Ignore any diff of Global Config and compare
    _ConfigComparator._unblock_section(["TAIPY"])
    config_diff = _ConfigComparator(_config_1, _config_2)

    config_diff._log_blocked_sections()
    assert caplog.text == ""
    assert config_diff.get("blocked_diff_sections") is None
    caplog.clear()

    unblocked_config_diff = config_diff["unblocked_diff_sections"]
    config_diff._log_unblocked_sections()
    assert len(caplog.text.strip().split("\n")) == 3
    assert len(unblocked_config_diff["added_items"]) == 1
    assert len(unblocked_config_diff["modified_items"]) == 2
    assert unblocked_config_diff.get("removed_items") is None
    caplog.clear()
