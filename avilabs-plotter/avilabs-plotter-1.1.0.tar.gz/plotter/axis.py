from typing import Tuple, List
from .font import Font


class Axis:
    def __init__(
        self,
        *,
        limits: Tuple[float, float]=None,
        ticks: List[float]=None,
        label: str=None,
        tick_labels: List[str]=None,
        font: Font=None
    ):
        self.limits = limits
        self.ticks = ticks
        self.label = label
        self.tick_labels = tick_labels
        self.font = font

    def _are_limits_compatible(self, other_limits):
        return (self.limits == other_limits or
                self.limits is None or
                other_limits is None)

    def _merge_limits(self, other_limits):
        if self.limits is None:
            self.limits = other_limits

    def _are_ticks_compatible(self, other_ticks):
        return (self.ticks == other_ticks or
                self.ticks is None or
                other_ticks is None)

    def _merge_ticks(self, other_ticks):
        if self.ticks is None:
            self.ticks = other_ticks

    def _are_labels_comptabile(self, other_label):
        return (self.label == other_label or
                self.label is None or
                other_label is None)

    def _merge_labels(self, other_label):
        if self.label is None:
            self.label = other_label

    def _are_tick_labels_compatible(self, other_tick_labels):
        return (self.tick_labels == other_tick_labels or
                self.tick_labels is None or
                other_tick_labels is None)

    def _merge_tick_labels(self, other_tick_labels):
        if self.tick_labels is None:
            self.tick_labels = other_tick_labels

    def _are_fonts_compatible(self, other_font):
        return (self.font is None or
                other_font is None or
                self.font == other_font)

    def _merge_fonts(self, other_font):
        if self.font is None:
            self.font = other_font

    def is_compatible(self, other):
        limits_ok = self._are_limits_compatible(other.limits)
        ticks_ok = self._are_ticks_compatible(other.ticks)
        label_ok = self._are_labels_comptabile(other.label)
        tick_labels_ok = self._are_tick_labels_compatible(other.tick_labels)
        fonts_ok = self._are_fonts_compatible(other.font)
        return limits_ok and ticks_ok and label_ok and tick_labels_ok and fonts_ok

    def merge_(self, other):
        if not self.is_compatible(other):
            raise ValueError('Trying to merge incompatible axes')

        self._merge_limits(other.limits)
        self._merge_ticks(other.ticks)
        self._merge_labels(other.label)
        self._merge_tick_labels(other.tick_labels)
        self._merge_fonts(other.font)