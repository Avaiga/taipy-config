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

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from ..common._template_handler import _TemplateHandler as _tpl


class GlobalAppConfig:
    """
    Configuration fields related to the global application.

    Parameters:
        root_folder (str): Path of the base folder for the taipy application. The default value is "./taipy/"
        storage_folder (str): Folder name used to store Taipy data. The default value is ".data/". It is used in
            conjunction with the `root_folder` field. That means the storage path is <root_folder><storage_folder>
            (The Default path is "./taipy/.data/").
        clean_entities_enabled (bool): Boolean field to activate/deactivate the clean entities feature. Default: false
        **properties: A dictionary of additional properties.
    """

    _ROOT_FOLDER_KEY = "root_folder"
    _DEFAULT_ROOT_FOLDER = "./taipy/"

    _STORAGE_FOLDER_KEY = "storage_folder"
    _DEFAULT_STORAGE_FOLDER = ".data/"

    _CLEAN_ENTITIES_ENABLED_KEY = "clean_entities_enabled"
    _DEFAULT_CLEAN_ENTITIES_ENABLED = False
    _CLEAN_ENTITIES_ENABLED_ENV_VAR = "TAIPY_CLEAN_ENTITIES_ENABLED"
    _CLEAN_ENTITIES_ENABLED_TEMPLATE = f"ENV[{_CLEAN_ENTITIES_ENABLED_ENV_VAR}]"

    _REPOSITORY_TYPE_KEY = "repository_type"
    _DEFAULT_REPOSITORY_TYPE = "filesystem"
    _REPOSITORY_PROPERTIES_KEY = "repository_properties"
    _DEFAULT_REPOSITORY_PROPERTIES = dict()

    def __init__(
        self,
        root_folder: str = None,
        storage_folder: str = None,
        clean_entities_enabled: Union[bool, str] = None,
        repository_type: str = None,
        repository_properties: Dict[str, Union[str, int]] = None,
        **properties,
    ):
        self._root_folder = root_folder
        self._storage_folder = storage_folder
        self._clean_entities_enabled = clean_entities_enabled
        self._repository_type = repository_type
        self._repository_properties = repository_properties
        self._properties = properties

    @property
    def storage_folder(self):
        return _tpl._replace_templates(self._storage_folder)

    @storage_folder.setter  # type: ignore
    def storage_folder(self, val):
        self._storage_folder = val

    @property
    def root_folder(self):
        return _tpl._replace_templates(self._root_folder)

    @root_folder.setter  # type: ignore
    def root_folder(self, val):
        self._root_folder = val

    @property
    def clean_entities_enabled(self):
        return _tpl._replace_templates(
            self._clean_entities_enabled, type=bool, required=False, default=self._DEFAULT_CLEAN_ENTITIES_ENABLED
        )

    @clean_entities_enabled.setter  # type: ignore
    def clean_entities_enabled(self, val):
        self._clean_entities_enabled = val
    
    @property
    def repository_type(self):
        return _tpl._replace_templates(self._repository_type)
    
    @repository_type.setter  # type: ignore
    def repository_type(self, val):
        print(f"setter {val}")
        self._repository_type = val
    

    @property
    def repository_properties(self):
        return {k: _tpl._replace_templates(v) for k, v in self._repository_properties.items()}

    @repository_properties.setter  # type: ignore
    def repository_properties(self, val):
        self._repository_properties = val

    @property
    def properties(self):
        return {k: _tpl._replace_templates(v) for k, v in self._properties.items()}

    @properties.setter  # type: ignore
    def properties(self, val):
        self._properties = val

    def __getattr__(self, item: str) -> Optional[Any]:
        return _tpl._replace_templates(self._properties.get(item))

    @classmethod
    def default_config(cls) -> GlobalAppConfig:
        config = GlobalAppConfig()
        config._root_folder = cls._DEFAULT_ROOT_FOLDER
        config._storage_folder = cls._DEFAULT_STORAGE_FOLDER
        config._clean_entities_enabled = cls._CLEAN_ENTITIES_ENABLED_TEMPLATE
        config._repository_type = cls._DEFAULT_REPOSITORY_TYPE
        config._repository_properties = cls._DEFAULT_REPOSITORY_PROPERTIES
        return config

    def _to_dict(self):
        as_dict = {}
        if self._root_folder:
            as_dict[self._ROOT_FOLDER_KEY] = self._root_folder
        if self._storage_folder:
            as_dict[self._STORAGE_FOLDER_KEY] = self._storage_folder
        if self._clean_entities_enabled is not None:
            as_dict[self._CLEAN_ENTITIES_ENABLED_KEY] = self._clean_entities_enabled
        if self._repository_type:
            as_dict[self._REPOSITORY_TYPE_KEY] = self._repository_type
        if self._repository_properties:
            as_dict[self._REPOSITORY_PROPERTIES_KEY] = self._repository_properties
        as_dict.update(self._properties)
        return as_dict

    @classmethod
    def _from_dict(cls, config_as_dict: Dict[str, Any]):
        config = GlobalAppConfig()
        config._root_folder = config_as_dict.pop(cls._ROOT_FOLDER_KEY, None)
        config._storage_folder = config_as_dict.pop(cls._STORAGE_FOLDER_KEY, None)
        config._clean_entities_enabled = config_as_dict.pop(cls._CLEAN_ENTITIES_ENABLED_KEY, None)
        config._repository_type = config_as_dict.pop(cls._REPOSITORY_TYPE_KEY, None)
        config._repository_properties = config_as_dict.pop(cls._REPOSITORY_PROPERTIES_KEY, None)
        config._properties = config_as_dict
        return config

    def _update(self, config_as_dict):
        self._root_folder = config_as_dict.pop(self._ROOT_FOLDER_KEY, self._root_folder)
        self._storage_folder = config_as_dict.pop(self._STORAGE_FOLDER_KEY, self._storage_folder)
        self._clean_entities_enabled = config_as_dict.pop(
            self._CLEAN_ENTITIES_ENABLED_KEY, self._clean_entities_enabled
        )
        self._repository_type = config_as_dict.pop(self._REPOSITORY_TYPE_KEY, self._repository_type)
        self._repository_properties = config_as_dict.pop(self._REPOSITORY_PROPERTIES_KEY, self._repository_properties)
        self._properties.update(config_as_dict)
