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

from src.taipy.config.data_node.scope import Scope
from src.taipy.config._config import _Config
from src.taipy.config.config import Config
from src.taipy.config.data_node.data_node_config import DataNodeConfig
from src.taipy.config.global_app.global_app_config import GlobalAppConfig
from src.taipy.config.job_execution.job_config import JobConfig
from src.taipy.config.pipeline.pipeline_config import PipelineConfig
from src.taipy.config.scenario.scenario_config import ScenarioConfig
from src.taipy.config.task.task_config import TaskConfig


def _test_default_global_app_config(global_config: GlobalAppConfig):
    assert global_config is not None
    assert not global_config.notification
    assert global_config.root_folder == "./taipy/"
    assert global_config.storage_folder == ".data/"
    assert global_config.broker_endpoint is None
    assert global_config._clean_entities_enabled is GlobalAppConfig._CLEAN_ENTITIES_ENABLED_TEMPLATE
    assert global_config.clean_entities_enabled is False
    assert len(global_config.properties) == 0


def _test_default_job_config(job_config: JobConfig):
    assert job_config is not None
    assert job_config.mode == JobConfig._DEFAULT_MODE


def _test_default_data_node_config(dn_config: DataNodeConfig):
    assert dn_config is not None
    assert dn_config.id is not None
    assert dn_config.storage_type == "pickle"
    assert dn_config.scope == Scope.SCENARIO
    assert not dn_config.cacheable
    assert len(dn_config.properties) == 1


def _test_default_task_config(task_config: TaskConfig):
    assert task_config is not None
    assert task_config.id is not None
    assert task_config.input_configs == []
    assert task_config.output_configs == []
    assert task_config.function is None
    assert len(task_config.properties) == 0


def _test_default_pipeline_config(pipeline_config: PipelineConfig):
    assert pipeline_config is not None
    assert pipeline_config.id is not None
    assert pipeline_config.task_configs == []
    assert len(pipeline_config.properties) == 0


def _test_default_scenario_config(scenario_config: ScenarioConfig):
    assert scenario_config is not None
    assert scenario_config.id is not None
    assert scenario_config.pipeline_configs == []
    assert len(scenario_config.properties) == 0


def test_default_configuration():
    default_config = _Config._default_config()
    assert default_config._unique_sections is not None
    assert len(default_config._unique_sections) == 0

    _test_default_global_app_config(default_config._global_config)
    _test_default_global_app_config(Config.global_config)
    _test_default_global_app_config(GlobalAppConfig().default_config())

    _test_default_job_config(default_config._job_config)
    _test_default_job_config(Config.job_config)
    _test_default_job_config(JobConfig().default_config())

    _test_default_data_node_config(default_config._data_nodes[_Config.DEFAULT_KEY])
    _test_default_data_node_config(Config.data_nodes[_Config.DEFAULT_KEY])
    _test_default_data_node_config(DataNodeConfig.default_config("DEFAULT_KEY"))
    assert len(default_config._data_nodes) == 1
    assert len(Config.data_nodes) == 1

    _test_default_task_config(default_config._tasks[_Config.DEFAULT_KEY])
    _test_default_task_config(Config.tasks[_Config.DEFAULT_KEY])
    _test_default_task_config(TaskConfig.default_config("DEFAULT_KEY"))
    assert len(default_config._tasks) == 1
    assert len(Config.tasks) == 1

    _test_default_pipeline_config(default_config._pipelines[_Config.DEFAULT_KEY])
    _test_default_pipeline_config(Config.pipelines[_Config.DEFAULT_KEY])
    _test_default_pipeline_config(PipelineConfig.default_config("DEFAULT_KEY"))
    assert len(default_config._pipelines) == 1
    assert len(Config.pipelines) == 1

    _test_default_scenario_config(default_config._scenarios[_Config.DEFAULT_KEY])
    _test_default_scenario_config(Config.scenarios[_Config.DEFAULT_KEY])
    _test_default_scenario_config(ScenarioConfig.default_config("DEFAULT_KEY"))
    assert len(default_config._scenarios) == 1
    assert len(Config.scenarios) == 1
