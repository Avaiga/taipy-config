import os
from unittest import mock

from src.taipy.config import Config
from src.taipy.config.data_node.scope import Scope
from src.taipy.config.scenario.frequency import Frequency
from tests.config.utils.named_temporary_file import NamedTemporaryFile


def test_read_write_configuration_file():
    expected_config = """
[TAIPY]
root_folder = "./taipy/"
storage_folder = ".data/"
clean_entities_enabled = "True:bool"

[unique_section_name]
attribute = "my_attribute"
prop = "my_prop"
prop_int = "1:int"
prop_bool = "False:bool"
prop_list = [ "p1",]
prop_scope = "SCENARIO"
prop_freq = "QUARTERLY"
baz = "ENV[QUX]"
quux = "ENV[QUUZ]:bool"
corge = [ "grault", "ENV[GARPLY]", "ENV[WALDO]:int", "3.0:float",]

[section_name.default]
attribute = "default_attribute"
prop_scope = "SCENARIO"
cacheable = "False:bool"
custom = "default_custom_prop"

[section_name.my_id]
attribute = "attribute"
prop_scope = "PIPELINE"
cacheable = "False:bool"
custom = "default_custom_prop"
    """.strip()
    tf = NamedTemporaryFile()
    with mock.patch.dict(
        os.environ, {"FOO": "in_memory", "QUX": "qux", "QUUZ": "true", "GARPLY": "garply", "WALDO": "17"}
    ):
        Config.configure_global_app(clean_entities_enabled=True)
        Config.configure_unique_section_for_tests(
            attribute="my_attribute",
            prop="my_prop",
            prop_int=1,
            prop_bool=False,
            prop_list=["p1", ],
            prop_scope=Scope.SCENARIO,
            prop_freq=Frequency.QUARTERLY,
            baz="ENV[QUX]",
            quux="ENV[QUUZ]:bool",
            corge=("grault", "ENV[GARPLY]", "ENV[WALDO]:int", 3.0))
        Config.export(tf.filename)
        actual_config = tf.read().strip()

        print(actual_config)

        # assert actual_config == expected_config
        # Config.load(tf.filename)
        # tf2 = NamedTemporaryFile()
        # Config.export(tf2.filename)
        # actual_config_2 = tf2.read().strip()
        # assert actual_config_2 == expected_config
