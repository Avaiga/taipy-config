from abc import ABC

from src.taipy.config import Section
from src.taipy.config.common._validate_id import _validate_id


class UniqueSection(Section, ABC):
    _UNIQUE_ID = "unique_id"

    def __init__(self, **properties):
        super().__init__(_validate_id(self._UNIQUE_ID), **properties)

