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
from typing import List

from .checker.issue import Issue
from .checker.issue_collector import IssueCollector
from .section import Section
from .unique_section import UniqueSection
from .config import Config
from .global_app.global_app_config import GlobalAppConfig
from .common.scope import Scope
from .common.frequency import Frequency


def _config_doc(func):
    def func_with_doc(section, attribute_name, default, configuration_methods):
        if True:  # TODO Find a condition that is always True except when it is running on taipy-doc.
            return func(section, attribute_name, default, configuration_methods)
        else:
            # TODO import and call an appropriate method from taipy-doc with params 'attribute_name'
            # 'Config.attribute_name' should be documented as an attribute of Config singleton to get the
            # 'section' config section.
            for exposed_configuration_method, configuration_method in configuration_methods:
                # TODO import and call an appropriate taipy-doc method with params 'exposed_configuration_method' and
                #  'configuration_method.__doc__'
                # 'Config.exposed_configuration_method' should be documented as a method of Config singleton.
                # the method documentation is in 'configuration_method.__doc__'
                print("Add documentation for method `Config.exposed_configuration_method` using value in "
                      "`configuration_method.__doc__`\n")
                print(configuration_method.__doc__)
            return func(section, attribute_name, default, configuration_methods)
        return func_with_doc


@_config_doc
def _inject_section(section_clazz, attribute_name: str, default: Section, configuration_methods: List[tuple]):
    Config._register_default(default)

    if issubclass(section_clazz, UniqueSection):
        setattr(Config, attribute_name, Config.unique_sections[section_clazz.name])
    elif issubclass(section_clazz, Section):
        setattr(Config, attribute_name, Config.sections[section_clazz.name])
    else:
        raise TypeError

    for exposed_configuration_method, configuration_method in configuration_methods:
        setattr(Config, exposed_configuration_method, configuration_method)
