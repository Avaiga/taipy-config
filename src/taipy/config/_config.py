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
from typing import Dict

from . import Section
from .data_node.data_node_config import DataNodeConfig
from .global_app.global_app_config import GlobalAppConfig
from .job_execution.job_config import JobConfig
from .pipeline.pipeline_config import PipelineConfig
from .scenario.scenario_config import ScenarioConfig
from .task.task_config import TaskConfig
from .unique_section import UniqueSection


class _Config:
    DEFAULT_KEY = "default"

    def __init__(self):
        self._sections: Dict[str, Dict[Section]] = {}
        self._unique_sections: Dict[str, UniqueSection] = {}
        self._global_config: GlobalAppConfig = GlobalAppConfig()
        # TO REFACTOR
        self._job_config: JobConfig = JobConfig()
        self._data_nodes: Dict[str, DataNodeConfig] = {}
        self._tasks: Dict[str, TaskConfig] = {}
        self._pipelines: Dict[str, PipelineConfig] = {}
        self._scenarios: Dict[str, ScenarioConfig] = {}
        # END REFACTOR

    @classmethod
    def _default_config(cls):
        config = _Config()
        # TO REFACTOR
        config._global_config = GlobalAppConfig.default_config()
        config._job_config = JobConfig().default_config()
        config._data_nodes = {cls.DEFAULT_KEY: DataNodeConfig.default_config(cls.DEFAULT_KEY)}
        config._tasks = {cls.DEFAULT_KEY: TaskConfig.default_config(cls.DEFAULT_KEY)}
        config._pipelines = {cls.DEFAULT_KEY: PipelineConfig.default_config(cls.DEFAULT_KEY)}
        config._scenarios = {cls.DEFAULT_KEY: ScenarioConfig.default_config(cls.DEFAULT_KEY)}
        # END REFACTOR
        return config

    def _update(self, other_config):
        if other_config._unique_sections:
            for section_name, other_section in other_config._unique_sections.items():
                if section := self._unique_sections.get(section_name, None):
                    section._update(other_section._to_dict())
                else:
                    self._unique_sections[section_name] = other_config._unique_sections[section_name]
        if other_config._sections:
            for section_name, other_non_unique_sections in other_config._sections.items():
                if non_unique_sections := self._sections.get(section_name, None):
                    self.__update_sections(non_unique_sections, other_non_unique_sections, None)
                else:
                    self._sections[section_name] = other_non_unique_sections
        # TO REFACTOR
        self._global_config._update(other_config._global_config._to_dict())
        self._job_config._update(other_config._job_config._to_dict())
        self.__update_sections(self._data_nodes, other_config._data_nodes, DataNodeConfig)
        self.__update_sections(self._tasks, other_config._tasks, TaskConfig)
        self.__update_sections(self._pipelines, other_config._pipelines, PipelineConfig)
        self.__update_sections(self._scenarios, other_config._scenarios, ScenarioConfig)
        # END REFACTOR

    def __update_sections(self, entity_config, other_entity_configs, _class):
        if self.DEFAULT_KEY in other_entity_configs:
            if self.DEFAULT_KEY in entity_config:
                entity_config[self.DEFAULT_KEY]._update(other_entity_configs[self.DEFAULT_KEY]._to_dict())
            else:
                entity_config[self.DEFAULT_KEY] = other_entity_configs[self.DEFAULT_KEY]
        for cfg_id, sub_config in other_entity_configs.items():
            if cfg_id != self.DEFAULT_KEY:
                if cfg_id in entity_config:
                    entity_config[cfg_id]._update(sub_config._to_dict(), entity_config.get(self.DEFAULT_KEY))
                else:
                    entity_config[cfg_id] = copy(sub_config)
                    entity_config[cfg_id]._update(sub_config._to_dict(), entity_config.get(self.DEFAULT_KEY))
