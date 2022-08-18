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

import json
import os
from typing import Any, Callable, Dict, List, Optional, Union

from .unique_section import UniqueSection
from .section import Section
from ..logger._taipy_logger import _TaipyLogger
from ._config import _Config
from ._toml_serializer import _TomlSerializer
from .checker._checker import _Checker
from .checker.issue_collector import IssueCollector
from .common._classproperty import _Classproperty
from .data_node.data_node_config import DataNodeConfig
from .common.scope import Scope
from .exceptions.exceptions import ConfigurationIssueError
from .global_app.global_app_config import GlobalAppConfig
from .pipeline.pipeline_config import PipelineConfig
from .common.frequency import Frequency
from .scenario.scenario_config import ScenarioConfig
from .section import Section
from .task.task_config import TaskConfig


class Config:
    """Configuration singleton."""

    _ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH = "TAIPY_CONFIG_PATH"
    __logger = _TaipyLogger._get_logger()
    _default_config = _Config._default_config()
    _python_config = _Config()
    _file_config = None
    _env_file_config = None
    _applied_config = _Config._default_config()
    _collector = IssueCollector()
    _serializer = _TomlSerializer()

    @_Classproperty
    def unique_sections(cls) -> Dict[str, UniqueSection]:
        """Return all unique sections."""
        return cls._applied_config._unique_sections

    @_Classproperty
    def sections(cls) -> Dict[str, Dict[str, Section]]:
        """Return all non unique sections."""
        return cls._applied_config._sections

    # TO REFACTOR
    @_Classproperty
    def global_config(cls) -> GlobalAppConfig:
        """Return configuration values related to the global application as a `GlobalAppConfig^`."""
        return cls._applied_config._global_config

    @_Classproperty
    def data_nodes(cls) -> Dict[str, DataNodeConfig]:
        """Return data node configs by config id."""
        return cls._applied_config._data_nodes

    @_Classproperty
    def tasks(cls) -> Dict[str, TaskConfig]:
        """Return task configs by config id."""
        return cls._applied_config._tasks

    @_Classproperty
    def pipelines(cls) -> Dict[str, PipelineConfig]:
        """Return pipeline configs by config id."""
        return cls._applied_config._pipelines

    @_Classproperty
    def scenarios(cls) -> Dict[str, ScenarioConfig]:
        """Return scenario configs by config id."""
        return cls._applied_config._scenarios
    # END REFACTOR

    @classmethod
    def load(cls, filename):
        """Load a configuration file.

        Parameters:
            filename (Union[str, Path]): The path of the toml configuration file to load.
        """
        cls.__logger.info(f"Loading configuration. Filename: '{filename}'")
        cls._file_config = cls._serializer._read(filename)
        cls.__compile_configs()
        cls.__logger.info(f"Configuration '{filename}' successfully loaded.")

    @classmethod
    def export(cls, filename):
        """Export a configuration.

        The export is done in a toml file.

        The exported configuration is a compilation from the three possible methods to configure
        the application: the python code configuration, the file configuration and the environment
        configuration.

        Parameters:
            filename (Union[str, Path]): The path of the file to export.
        Note:
            If _filename_ already exists, it is overwritten.
        """
        cls._serializer._write(cls._applied_config, filename)

    @classmethod
    def _export_code_config(cls, filename):
        cls._serializer._write(cls._python_config, filename)

    @classmethod
    def configure_global_app(
        cls,
        root_folder: str = None,
        storage_folder: str = None,
        clean_entities_enabled: Union[bool, str] = None,
        **properties,
    ) -> GlobalAppConfig:
        """Configure the global application.

        Parameters:
            root_folder (Optional[str]): The path of the base folder for the Taipy application.
            storage_folder (Optional[str]): The folder name used to store Taipy data.
                It is used in conjunction with the root_folder field: the storage path is
                "<root_folder><storage_folder>".
            clean_entities_enabled (Optional[str]): The field to activate or deactivate the
                'clean entities' feature. The default value is False.
        Returns:
            GlobalAppConfig^: The global application configuration.
        """
        glob_cfg = GlobalAppConfig(root_folder, storage_folder, clean_entities_enabled, **properties)
        if cls._python_config._global_config is None:
            cls._python_config._global_config = glob_cfg
        else:
            cls._python_config._global_config._update(glob_cfg._to_dict())
        cls.__compile_configs()
        return cls._applied_config._global_config

    # TO REFACTOR
    @classmethod
    def configure_data_node(
        cls,
        id: str,
        storage_type: str = DataNodeConfig._DEFAULT_STORAGE_TYPE,
        scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ) -> DataNodeConfig:
        """Configure a new data node configuration.

        Parameters:
            id (str): The unique identifier of the new data node configuration.
            storage_type (str): The data node configuration storage type. The possible values
                are _"pickle"_ (which the default value, unless it has been overloaded by the
                _storage_type_ value set in the default data node configuration
                (see `(Config.)configure_default_data_node()^`)), _"csv"_, _"excel"_, _"sql"_,
                _"in_memory"_, or _"generic"_.
            scope (Scope^): The scope of the data node configuration. The default value is
                `Scope.SCENARIO` (or the one specified in
                `(Config.)configure_default_data_node()^`).
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            DataNodeConfig^: The new data node configuration.
        """
        dn_config = DataNodeConfig(id, storage_type, scope, **properties)
        cls._python_config._data_nodes[dn_config.id] = dn_config
        cls.__compile_configs()
        return cls._applied_config._data_nodes[dn_config.id]

    @classmethod
    def configure_default_data_node(
        cls, storage_type: str, scope=DataNodeConfig._DEFAULT_SCOPE, **properties
    ) -> DataNodeConfig:
        """Configure the default values for data node configurations.

        This function creates the _default data node configuration_ object,
        where all data node configuration objects will find their default
        values when needed.

        Parameters:
            storage_type (str): The default storage type for all data node configurations.
                The possible values are _"pickle"_ (the default value), _"csv"_, _"excel"_,
                _"sql"_, _"in_memory"_, _"json"_ or _"generic"_.
            scope (Scope^): The default scope fot all data node configurations.
                The default value is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            DataNodeConfig^: The default data node configuration.
        """
        data_node_config = DataNodeConfig(_Config.DEFAULT_KEY, storage_type, scope, **properties)
        cls._python_config._data_nodes[_Config.DEFAULT_KEY] = data_node_config
        cls.__compile_configs()
        return cls._applied_config._data_nodes[_Config.DEFAULT_KEY]

    @classmethod
    def configure_task(
        cls,
        id: str,
        function,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        **properties,
    ) -> TaskConfig:
        """Configure a new task configuration.

        Parameters:
            id (str): The unique identifier of this task configuration.
            function (Callable): The python function called by Taipy to run the task.
            input (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                function input data node configurations. This can be a unique data node
                configuration if there is a single input data node, or None if there are none.
            output (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                function output data node configurations. This can be a unique data node
                configuration if there is a single output data node, or None if there are none.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            TaskConfig^: The new task configuration.
        """
        task_config = TaskConfig(id, function, input, output, **properties)
        cls._python_config._tasks[task_config.id] = task_config
        cls.__compile_configs()
        return cls._applied_config._tasks[task_config.id]

    @classmethod
    def configure_default_task(
        cls,
        function,
        input: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        output: Optional[Union[DataNodeConfig, List[DataNodeConfig]]] = None,
        **properties,
    ) -> TaskConfig:
        """Configure the default values for task configurations.

        This function creates the _default task configuration_ object,
        where all task configuration objects will find their default
        values when needed.

        Parameters:
            function (Callable): The python function called by Taipy to run the task.
            input (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                input data node configurations. This can be a unique data node
                configuration if there is a single input data node, or None if there are none.
            output (Optional[Union[DataNodeConfig^, List[DataNodeConfig^]]]): The list of the
                output data node configurations. This can be a unique data node
                configuration if there is a single output data node, or None if there are none.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            TaskConfig^: The default task configuration.
        """
        task_config = TaskConfig(_Config.DEFAULT_KEY, function, input, output, **properties)
        cls._python_config._tasks[task_config.id] = task_config
        cls.__compile_configs()
        return cls._applied_config._tasks[_Config.DEFAULT_KEY]

    @classmethod
    def configure_pipeline(
        cls, id: str, task_configs: Union[TaskConfig, List[TaskConfig]], **properties
    ) -> PipelineConfig:
        """Configure a new pipeline configuration.

        Parameters:
            id (str): The unique identifier of the new pipeline configuration.
            task_configs (Union[TaskConfig^, List[TaskConfig^]]): The list of the task
                configurations that make this new pipeline. This can be a single task
                configuration object is this pipeline holds a single task.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            PipelineConfig^: The new pipeline configuration.
        """
        pipeline_config = PipelineConfig(id, task_configs, **properties)
        cls._python_config._pipelines[pipeline_config.id] = pipeline_config
        cls.__compile_configs()
        return cls._applied_config._pipelines[pipeline_config.id]

    @classmethod
    def configure_default_pipeline(
        cls, task_configs: Union[TaskConfig, List[TaskConfig]], **properties
    ) -> PipelineConfig:
        """Configure the default values for pipeline configurations.

        This function creates the _default pipeline configuration_ object,
        where all pipeline configuration objects will find their default
        values when needed.

        Parameters:
            task_configs (Union[TaskConfig^, List[TaskConfig^]]): The list of the task
                configurations that make the default pipeline configuration. This can be
                a single task configuration object is this pipeline holds a single task.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            PipelineConfig^: The default pipeline configuration.
        """
        pipeline_config = PipelineConfig(_Config.DEFAULT_KEY, task_configs, **properties)
        cls._python_config._pipelines[_Config.DEFAULT_KEY] = pipeline_config
        cls.__compile_configs()
        return cls._applied_config._pipelines[_Config.DEFAULT_KEY]

    @classmethod
    def configure_scenario(
        cls,
        id: str,
        pipeline_configs: List[PipelineConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ) -> ScenarioConfig:
        """Configure a new scenario configuration.

        Parameters:
            id (str): The unique identifier of the new scenario configuration.
            pipeline_configs (List[PipelineConfig^]): The list of pipeline configurations used
                by this new scenario configuration.
            frequency (Optional[Frequency^]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this
                configuration. Based on this frequency each scenario will be attached to the
                relevant cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of
                functions used to compare scenarios. A comparator function is attached to a
                scenario's data node configuration. The key of the dictionary parameter
                corresponds to the data node configuration id. During the scenarios'
                comparison, each comparator is applied to all the data nodes instantiated from
                the data node configuration attached to the comparator. See
                `(taipy.)compare_scenarios()^` more more details.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            ScenarioConfig^: The new scenario configuration.
        """
        scenario_config = ScenarioConfig(
            id, pipeline_configs, frequency=frequency, comparators=comparators, **properties
        )
        cls._python_config._scenarios[scenario_config.id] = scenario_config
        cls.__compile_configs()
        return cls._applied_config._scenarios[scenario_config.id]

    @classmethod
    def configure_scenario_from_tasks(
        cls,
        id: str,
        task_configs: List[TaskConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        pipeline_id: Optional[str] = None,
        **properties,
    ) -> ScenarioConfig:
        """Configure a new scenario configuration made of a single new pipeline configuration.

        A new pipeline configuration is created as well. If _pipeline_id_ is not provided,
        the new pipeline configuration identifier is set to the scenario configuration identifier
        post-fixed by '_pipeline'.

        Parameters:
            id (str): The unique identifier of the scenario configuration.
            task_configs (List[TaskConfig^]): The list of task configurations used by the
                new pipeline configuration that is created.
            frequency (Optional[Frequency^]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this
                configuration. Based on this frequency each scenario will be attached to the
                relevant cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of
                functions used to compare scenarios. A comparator function is attached to a
                scenario's data node configuration. The key of the dictionary parameter
                corresponds to the data node configuration id. During the scenarios'
                comparison, each comparator is applied to all the data nodes instantiated from
                the data node configuration attached to the comparator. See
                `(taipy.)compare_scenarios()` more more details.
            pipeline_id (str): The identifier of the new pipeline configuration to be
                configured.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            ScenarioConfig^: The new scenario configuration.
        """
        if not pipeline_id:
            pipeline_id = f"{id}_pipeline"
        pipeline_config = cls.configure_pipeline(pipeline_id, task_configs, **properties)
        return cls.configure_scenario(id, [pipeline_config], frequency=frequency, comparators=comparators, **properties)

    @classmethod
    def configure_default_scenario(
        cls,
        pipeline_configs: List[PipelineConfig],
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ):
        """Configure the default values for scenario configurations.

        This function creates the _default scenario configuration_ object,
        where all scenario configuration objects will find their default
        values when needed.

        Parameters:
            pipeline_configs (List[PipelineConfig^]): The list of pipeline configurations used
                by this scenario configuration.
            frequency (Optional[Frequency^]): The scenario frequency.
                It corresponds to the recurrence of the scenarios instantiated from this
                configuration. Based on this frequency each scenario will be attached to
                the relevant cycle.
            comparators (Optional[Dict[str, Union[List[Callable], Callable]]]): The list of
                functions used to compare scenarios. A comparator function is attached to a
                scenario's data node configuration. The key of the dictionary parameter
                corresponds to the data node configuration id. During the scenarios'
                comparison, each comparator is applied to all the data nodes instantiated from
                the data node configuration attached to the comparator. See
                `taipy.compare_scenarios()^` more more details.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            ScenarioConfig^: The default scenario configuration.
        """
        scenario_config = ScenarioConfig(
            _Config.DEFAULT_KEY, pipeline_configs, frequency=frequency, comparators=comparators, **properties
        )
        cls._python_config._scenarios[_Config.DEFAULT_KEY] = scenario_config
        cls.__compile_configs()
        return cls._applied_config._scenarios[_Config.DEFAULT_KEY]

    @classmethod
    def configure_csv_data_node(
        cls,
        id: str,
        default_path: str = None,
        has_header: bool = True,
        scope=DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ):
        """Configure a new CSV data node configuration.

        Parameters:
            id (str): The unique identifier of the new CSV data node configuration.
            default_path (str): The default path of the CSV file.
            has_header (bool): If True, indicates that the CSV file has a header.
            scope (Scope^): The scope of the CSV data node configuration. The default value
                is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            DataNodeConfig^: The new CSV data node configuration.
        """
        return cls.configure_data_node(
            id,
            DataNodeConfig._STORAGE_TYPE_VALUE_CSV,
            scope=scope,
            default_path=default_path,
            has_header=has_header,
            **properties,
        )

    @classmethod
    def configure_json_data_node(
        cls,
        id: str,
        default_path: str = None,
        encoder: json.JSONEncoder = None,
        decoder: json.JSONDecoder = None,
        scope=DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ):
        """Configure a new JSON data node configuration.

        Parameters:
            id (str): The unique identifier of the new JSON data node configuration.
            default_path (str): The default path of the JSON file.
            encoder (json.JSONEncoder): The JSON encoder used to write data into the JSON file.
            decoder (json.JSONDecoder): The JSON decoder used to read data from the JSON file.
            scope (Scope^): The scope of the JSON data node configuration. The default value
                is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            DataNodeConfig^: The new JSON data node configuration.
        """
        return cls.configure_data_node(
            id,
            DataNodeConfig._STORAGE_TYPE_VALUE_JSON,
            scope=scope,
            default_path=default_path,
            encoder=encoder,
            decoder=decoder,
            **properties,
        )

    @classmethod
    def configure_excel_data_node(
        cls,
        id: str,
        default_path: str = None,
        has_header: bool = True,
        sheet_name: Union[List[str], str] = None,
        scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ):
        """Configure a new Excel data node configuration.

        Parameters:
            id (str): The unique identifier of the new Excel data node configuration.
            default_path (str): The path of the Excel file.
            has_header (bool): If True, indicates that the Excel file has a header.
            sheet_name (Union[List[str], str]): The list of sheet names to be used. This
                can be a unique name.
            scope (Scope^): The scope of the Excel data node configuration. The default
                value is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            DataNodeConfig^: The new CSV data node configuration.
        """

        return cls.configure_data_node(
            id,
            DataNodeConfig._STORAGE_TYPE_VALUE_EXCEL,
            scope=scope,
            default_path=default_path,
            has_header=has_header,
            sheet_name=sheet_name,
            **properties,
        )

    @classmethod
    def configure_generic_data_node(
        cls,
        id: str,
        read_fct: Callable = None,
        write_fct: Callable = None,
        read_fct_params: List = None,
        write_fct_params: List = None,
        scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ):
        """Configure a new generic data node configuration.

        Parameters:
            id (str): The unique identifier of the new generic data node configuration.
            read_fct (Optional[Callable]): The Python function called to read the data.
            write_fct (Optional[Callable]): The Python function called to write the data.
                The provided function must have at least one parameter that receives the data
                to be written.
            read_fct_params (Optional[List]): The parameters that are passed to _read_fct_
                to read the data.
            write_fct_params (Optional[List]): The parameters that are passed to _write_fct_
                to write the data.
            scope (Optional[Scope^]): The scope of the Generic data node configuration.
                The default value is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            DataNodeConfig^: The new Generic data node configuration.
        """
        return cls.configure_data_node(
            id,
            DataNodeConfig._STORAGE_TYPE_VALUE_GENERIC,
            scope=scope,
            read_fct=read_fct,
            write_fct=write_fct,
            read_fct_params=read_fct_params,
            write_fct_params=write_fct_params,
            **properties,
        )

    @classmethod
    def configure_in_memory_data_node(
        cls, id: str, default_data: Optional[Any] = None, scope: Scope = DataNodeConfig._DEFAULT_SCOPE, **properties
    ):
        """Configure a new _in_memory_ data node configuration.

        Parameters:
            id (str): The unique identifier of the new in_memory data node configuration.
            default_data (Optional[Any]): The default data of the data nodes instantiated from
                this in_memory data node configuration.
            scope (Scope^): The scope of the in_memory data node configuration. The default
                value is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            DataNodeConfig^: The new _in_memory_ data node configuration.
        """
        return cls.configure_data_node(
            id, DataNodeConfig._STORAGE_TYPE_VALUE_IN_MEMORY, scope=scope, default_data=default_data, **properties
        )

    @classmethod
    def configure_pickle_data_node(
        cls, id: str, default_data: Optional[Any] = None, scope: Scope = DataNodeConfig._DEFAULT_SCOPE, **properties
    ):
        """Configure a new pickle data node configuration.

        Parameters:
            id (str): The unique identifier of the new pickle data node configuration.
            default_data (Optional[Any]): The default data of the data nodes instantiated from
                this pickle data node configuration.
            scope (Scope^): The scope of the pickle data node configuration. The default value
                is `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            DataNodeConfig^: The new pickle data node configuration.
        """
        return cls.configure_data_node(
            id, DataNodeConfig._STORAGE_TYPE_VALUE_PICKLE, scope=scope, default_data=default_data, **properties
        )

    @classmethod
    def configure_sql_data_node(
        cls,
        id: str,
        db_username: str,
        db_password: str,
        db_name: str,
        db_engine: str,
        read_query: str,
        write_table: str = None,
        db_port: int = 1433,
        db_host: str = "localhost",
        db_driver: str = "ODBC Driver 17 for SQL Server",
        scope: Scope = DataNodeConfig._DEFAULT_SCOPE,
        **properties,
    ):
        """Configure a new SQL data node configuration.

        Parameters:
            id (str): The unique identifier of the new SQL data node configuration.
            db_username (str): The database username.
            db_password (str): The database password.
            db_name (str): The database name.
            db_engine (str): The database engine. Possible values are _"sqlite"_ or _"mssql"_.
            read_query (str): The SQL query string used to read the data from the database.
            write_table (str): The name of the table in the database to write the data to.
            db_port (int): The database port. The default value is 1433.
            db_host (str): The database host. The default value is _"localhost"_.
            db_driver (str): The database driver. The default value is
                _"ODBC Driver 17 for SQL Server"_.
            scope (Scope^): The scope of the SQL data node configuration. The default value is
                `Scope.SCENARIO`.
            **properties (Dict[str, Any]): A keyworded variable length list of additional
                arguments.
        Returns:
            DataNodeConfig^: The new SQL data node configuration.
        """
        return cls.configure_data_node(
            id,
            DataNodeConfig._STORAGE_TYPE_VALUE_SQL,
            scope=scope,
            db_username=db_username,
            db_password=db_password,
            db_name=db_name,
            db_host=db_host,
            db_engine=db_engine,
            db_driver=db_driver,
            read_query=read_query,
            write_table=write_table,
            db_port=db_port,
            **properties,
        )
    # END REFACTOR

    @classmethod
    def check(cls) -> IssueCollector:
        """Check configuration.

        This method logs issue messages and returns an issue collector.

        Returns:
            IssueCollector^: Collector containing the info, warning and error issues.
        """
        cls._collector = _Checker._check(cls._applied_config)
        cls.__log_message(cls)
        return cls._collector

    @classmethod
    def _register_default(cls, default_section: Section):
        if isinstance(default_section, UniqueSection):
            if cls._default_config._unique_sections.get(default_section.name, None):
                cls._default_config._unique_sections[default_section.name]._update(default_section._to_dict())
            else:
                cls._default_config._unique_sections[default_section.name] = default_section
        else:
            if def_sections := cls._default_config._sections.get(default_section.name, None):
                if def_sections.get(default_section.id, None):
                    def_sections[default_section.id]._update(default_section._to_dict())
                else:
                    def_sections[default_section.id] = default_section
            else:
                cls._default_config._sections[default_section.name] = {default_section.id: default_section}
        cls._serializer._section_class[default_section.name] = default_section.__class__
        cls.__compile_configs()

    @classmethod
    def _register(cls, section):
        if isinstance(section, UniqueSection):
            if cls._python_config._unique_sections.get(section.name, None):
                cls._python_config._unique_sections[section.name]._update(section._to_dict())
            else:
                cls._python_config._unique_sections[section.name] = section
        else:
            if sections := cls._python_config._sections.get(section.name, None):
                if sections.get(section.id, None):
                    sections[section.id]._update(section._to_dict())
                else:
                    sections[section.id] = section
            else:
                cls._python_config._sections[section.name] = {section.id: section}
        cls._serializer._section_class[section.name] = section.__class__
        cls.__compile_configs()

    @classmethod
    def _load_environment_file_config(cls):
        if config_filename := os.environ.get(cls._ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH):
            cls.__logger.info(f"Loading configuration provided by environment variable. Filename: '{config_filename}'")
            cls._env_file_config = cls._serializer._read(config_filename)
            cls.__logger.info(f"Configuration '{config_filename}' successfully loaded.")

    @classmethod
    def __compile_configs(cls):
        Config._load_environment_file_config()
        cls._applied_config = _Config._default_config()
        if cls._default_config:
            cls._applied_config._update(cls._default_config)
        if cls._python_config:
            cls._applied_config._update(cls._python_config)
        if cls._file_config:
            cls._applied_config._update(cls._file_config)
        if cls._env_file_config:
            cls._applied_config._update(cls._env_file_config)

    @classmethod
    def __log_message(cls, config):
        for issue in config._collector._warnings:
            cls.__logger.warning(str(issue))
        for issue in config._collector._infos:
            cls.__logger.info(str(issue))
        for issue in config._collector._errors:
            cls.__logger.error(str(issue))
        if len(config._collector._errors) != 0:
            raise ConfigurationIssueError("Configuration issues found.")


Config._load_environment_file_config()
