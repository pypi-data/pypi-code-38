"""Advanced class definition."""
from typing import List, Optional


class Advanced:
    """Class with advanced data types."""

    array: List[str]
    optional: Optional[str]
    _private: bool

    @property
    def dynamic_value(self) -> int:
        """Dynamic property"""
        return 5

    @property
    def not_annotated_property(self):
        """This property has no annotation"""
        return None
