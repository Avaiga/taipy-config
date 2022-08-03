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

import os
from unittest import mock

from src.taipy.config.config import Config
from src.taipy.config.common.scope import Scope
from src.taipy.config.common.frequency import Frequency
from tests.config.utils.named_temporary_file import NamedTemporaryFile


def test_write_configuration_file_CORE():
    expected_config = """
[TAIPY]
root_folder = "./taipy/"
storage_folder = ".data/"
clean_entities_enabled = "True:bool"

[JOB]
mode = "standalone"
nb_of_workers = "2:int"

[unique_section_name]
attribute = "default_attribute"

[DATA_NODE.default]
storage_type = "in_memory"
scope = "SCENARIO:SCOPE"
cacheable = "False:bool"
custom = "default_custom_prop"

[DATA_NODE.dn1]
storage_type = "pickle"
scope = "PIPELINE:SCOPE"
cacheable = "False:bool"
custom = "custom property"
default_data = "dn1"

[DATA_NODE.dn2]
storage_type = "ENV[FOO]"
scope = "SCENARIO:SCOPE"
cacheable = "False:bool"
custom = "default_custom_prop"
foo = "bar"
default_data = "dn2"
baz = "ENV[QUX]"
quux = "ENV[QUUZ]:bool"
corge = [ "grault", "ENV[GARPLY]", "ENV[WALDO]:int", "3.0:float",]

[TASK.default]
inputs = []
outputs = []

[TASK.t1]
inputs = [ "dn1",]
function = "<built-in function print>"
outputs = [ "dn2",]
description = "t1 description"

[PIPELINE.default]
tasks = []

[PIPELINE.p1]
tasks = [ "t1",]
cron = "daily"

[SCENARIO.default]
pipelines = []
frequency = "QUARTERLY:FREQUENCY"
owner = "Michel Platini"

[SCENARIO.s1]
pipelines = [ "p1",]
frequency = "QUARTERLY:FREQUENCY"
owner = "Raymond Kopa"

[section_name.default]
attribute = "default_attribute"
prop = "default_prop"
prop_int = "0:int"
    """.strip()
    tf = NamedTemporaryFile()
    with mock.patch.dict(
        os.environ, {"FOO": "in_memory", "QUX": "qux", "QUUZ": "true", "GARPLY": "garply", "WALDO": "17"}
    ):
        Config.configure_global_app(clean_entities_enabled=True)
        Config.configure_job_executions(mode="standalone", nb_of_workers=2)
        Config.configure_default_data_node(storage_type="in_memory", custom="default_custom_prop")
        dn1_cfg_v2 = Config.configure_data_node(
            "dn1", storage_type="pickle", scope=Scope.PIPELINE, default_data="dn1", custom="custom property"
        )
        dn2_cfg_v2 = Config.configure_data_node(
            "dn2",
            storage_type="ENV[FOO]",
            foo="bar",
            default_data="dn2",
            baz="ENV[QUX]",
            quux="ENV[QUUZ]:bool",
            corge=("grault", "ENV[GARPLY]", "ENV[WALDO]:int", 3.0),
        )
        t1_cfg_v2 = Config.configure_task("t1", print, dn1_cfg_v2, dn2_cfg_v2, description="t1 description")
        p1_cfg_v2 = Config.configure_pipeline("p1", t1_cfg_v2, cron="daily")
        Config.configure_default_scenario([], Frequency.QUARTERLY, owner="Michel Platini")
        Config.configure_scenario("s1", p1_cfg_v2, frequency=Frequency.QUARTERLY, owner="Raymond Kopa")
        Config.export(tf.filename)
        actual_config = tf.read().strip()

        assert actual_config == expected_config
        Config.load(tf.filename)
        tf2 = NamedTemporaryFile()
        Config.export(tf2.filename)
        actual_config_2 = tf2.read().strip()
        assert actual_config_2 == expected_config


def test_read_configuration_file_CORE():
    file_config = NamedTemporaryFile(
        """
        [DATA_NODE.default]
        has_header = true

        [DATA_NODE.my_datanode]
        path = "/data/csv"

        [DATA_NODE.my_datanode2]
        path = "/data2/csv"

        [TASK.my_task]
        inputs = ["my_datanode"]
        function = "<built-in function print>"
        outputs = ["my_datanode2"]
        description = "task description"

        [PIPELINE.my_pipeline]
        tasks = [ "my_Task",]
        cron = "daily"

        [SCENARIO.my_scenario]
        pipelines = [ "my_pipeline",]
        owner = "John Doe"
        """
    )
    Config.load(file_config.filename)
    data_node_1_config = Config.configure_data_node(id="my_datanode")
    data_node_2_config = Config.configure_data_node(id="my_datanode2")
    task_config = Config.configure_task("my_task", print, data_node_1_config, data_node_2_config)
    pipeline_config = Config.configure_pipeline("my_pipeline", task_config)
    Config.configure_scenario("my_scenario", [pipeline_config])

    assert len(Config.data_nodes) == 3
    assert Config.data_nodes["my_datanode"].path == "/data/csv"
    assert Config.data_nodes["my_datanode2"].path == "/data2/csv"
    assert Config.data_nodes["my_datanode"].id == "my_datanode"
    assert Config.data_nodes["my_datanode2"].id == "my_datanode2"

    assert len(Config.tasks) == 2
    assert Config.tasks["my_task"].id == "my_task"
    assert Config.tasks["my_task"].description == "task description"

    assert len(Config.pipelines) == 2
    assert Config.pipelines["my_pipeline"].id == "my_pipeline"
    assert Config.pipelines["my_pipeline"].cron == "daily"

    assert len(Config.scenarios) == 2
    assert Config.scenarios["my_scenario"].id == "my_scenario"
    assert Config.scenarios["my_scenario"].owner == "John Doe"
