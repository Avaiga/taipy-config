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

import pytest

from src.taipy.config.config import Config
from src.taipy.config.exceptions.exceptions import ConfigurationUpdateBlocked, InconsistentEnvVariableError
from src.taipy.config.global_app.global_app_config import GlobalAppConfig


def test_global_config_with_env_variable_value():
    with mock.patch.dict(os.environ, {"FOO": "bar", "BAZ": "qux"}):
        Config.configure_global_app(root_folder="ENV[FOO]", storage_folder="ENV[BAZ]")
        assert Config.global_config.root_folder == "bar"
        assert Config.global_config._root_folder == "ENV[FOO]"
        assert Config.global_config.storage_folder == "qux"
        assert Config.global_config._storage_folder == "ENV[BAZ]"


def test_clean_entities_enabled_default():
    Config.configure_global_app()
    assert Config.global_config.clean_entities_enabled is GlobalAppConfig._DEFAULT_CLEAN_ENTITIES_ENABLED
    with mock.patch.dict(os.environ, {f"{GlobalAppConfig._CLEAN_ENTITIES_ENABLED_ENV_VAR}": "true"}):
        Config.configure_global_app()  # Trigger config compilation
        assert Config.global_config.clean_entities_enabled is True
    with mock.patch.dict(os.environ, {f"{GlobalAppConfig._CLEAN_ENTITIES_ENABLED_ENV_VAR}": "false"}):
        Config.configure_global_app()
        assert Config.global_config.clean_entities_enabled is False
    with mock.patch.dict(os.environ, {f"{GlobalAppConfig._CLEAN_ENTITIES_ENABLED_ENV_VAR}": "foo"}):
        with pytest.raises(InconsistentEnvVariableError):
            Config.configure_global_app()
            assert Config.global_config.clean_entities_enabled is False


def test_default_global_app_config():
    global_config = Config.global_config
    assert global_config is not None
    assert not global_config.notification
    assert global_config.root_folder == "./taipy/"
    assert global_config.storage_folder == ".data/"
    assert global_config._clean_entities_enabled is GlobalAppConfig._CLEAN_ENTITIES_ENABLED_TEMPLATE
    assert global_config.clean_entities_enabled is False

    assert global_config.repository_type == "filesystem"
    assert global_config.repository_properties == {}
    assert len(global_config.properties) == 0


def test_block_update_global_app_config():
    Config.block_update()

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.configure_global_app(root_folder="./new_root_folder/", storage_folder=".new_storage/")

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.configure_global_app(root_folder="./new_root_folder/", storage_folder=".new_storage/")

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.global_config.root_folder = "./new_root_folder/"

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.global_config.storage_folder = ".new_storage/"

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.global_config.clean_entities_enabled = True

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.global_config.repository_type = "mongo"

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.global_config.repository_properties = {}

    with pytest.raises(ConfigurationUpdateBlocked):
        Config.global_config.properties = {"foo": "bar"}

    global_config = Config.global_config

    # Test if the global_config stay as default
    assert global_config.root_folder == "./taipy/"
    assert global_config.storage_folder == ".data/"
    assert global_config.clean_entities_enabled is False
    assert global_config.repository_type == "filesystem"
    assert global_config.repository_properties == {}
    assert len(global_config.properties) == 0
