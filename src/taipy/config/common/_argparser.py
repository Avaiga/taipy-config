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

import argparse


class _Argparser:
    """Argument parser for Taipy application."""

    # The conflict_handler is set to "resolve" to override conflict arguments
    parser = argparse.ArgumentParser(conflict_handler="resolve")

    @classmethod
    def _add_groupparser(cls, title: str, description: str = ""):
        """Create a new group for arguments and return a argparser handle."""
        return cls.parser.add_argument_group(title=title, description=description)

    @classmethod
    def _parse(cls):
        """Parse and return only known arguments."""
        args, unknown_args = cls.parser.parse_known_args()
        return args
