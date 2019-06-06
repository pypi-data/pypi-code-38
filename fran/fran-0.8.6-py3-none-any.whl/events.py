from collections import defaultdict
from enum import Enum
from typing import NamedTuple, Dict, DefaultDict, List, Tuple, Iterator
import logging

import numpy as np
import pandas as pd

from fran.common import load_results, dump_results, df_to_str, Special

logger = logging.getLogger(__name__)


class Action(Enum):
    INSERT = "INSERT"
    DELETE = "DELETE"

    def invert(self):
        if self == Action.INSERT:
            return Action.DELETE
        else:
            return Action.INSERT

    def __str__(self):
        return self.value


class LoggedKeyEvent(NamedTuple):
    action: Action
    key: str
    frame: int
    note: str = ""

    def invert(self):
        return LoggedKeyEvent(self.action.invert(), self.key, self.frame, self.note)

    def __str__(self):
        return "{} {} @ {} ({})".format(*self)

    def copy(self, **kwargs):
        d = self._asdict()
        d.update(kwargs)
        return LoggedKeyEvent(**d)


class EventLogger:
    def __init__(self, key_mapping=None):
        self.logger = logger.getChild(type(self).__name__)

        self.key_mapping: Dict[str, str] = key_mapping or dict()
        self.events: DefaultDict[str, Dict[int, str]] = defaultdict(dict)

        self.past: List[LoggedKeyEvent] = []
        self.future: List[LoggedKeyEvent] = []
        self.changed = True

    def to_dict(self):
        return {k: dict(v) for k, v in self.events.items() if v}

    @classmethod
    def from_dict(cls, d):
        el = cls()
        for k, v in d.items():
            if v:
                el.events[k] = {int(ki): vi for ki, vi in v.items()}
        return el

    def is_before(self, val):
        return val == Special.BEFORE

    def is_after(self, val):
        return val == Special.AFTER

    def name(self, key):
        key = key.lower()
        return self.key_mapping.get(key, key)

    def keys(self):
        return {k.lower() for k in self.events}

    def starts(self):
        for k in self.keys():
            yield k, self.events[k]

    def stops(self):
        for k in self.keys():
            yield k, self.events[k.upper()]

    def _do(self, to_do: LoggedKeyEvent):
        if to_do.action == Action.INSERT:
            return self._insert(to_do)
        else:
            return self._delete(to_do)

    def _insert(self, to_insert: LoggedKeyEvent) -> LoggedKeyEvent:
        self.changed = True
        note = to_insert.note or self.events[to_insert.key].get(to_insert.frame, "")
        to_insert.copy(action=Action.INSERT, note=note)
        self.events[to_insert.key][to_insert.frame] = note
        return to_insert

    def insert(self, key: str, frame: int, note=""):
        done = self._insert(LoggedKeyEvent(Action.INSERT, key, frame, note))
        self.past.append(done)
        self.future.clear()
        self.logger.info("Logged %s", done)
        return done

    def _delete(self, to_do):
        self.changed = True
        if to_do.frame is None:
            return None
        note = self.events[to_do.key].pop(to_do.frame, None)
        if note is None:
            return None
        else:
            return to_do.copy(action=Action.DELETE, note=note)

    def delete(self, key, frame):
        done = self._delete(LoggedKeyEvent(action=Action.DELETE, key=key, frame=frame))

        if done is None:
            self.logger.info("Nothing to delete")
            return None
        else:
            self.future.clear()
            self.past.append(done)
            self.logger.info("Logged %s", done)
            return done

    def undo(self):
        if not self.past:
            self.logger.info("Nothing to undo")
            return None
        to_undo = self.past.pop()
        done = self._do(to_undo.invert())
        self.future.append(done)

        self.logger.info("Undid %s", to_undo)

    def redo(self):
        if not self.future:
            self.logger.info("Nothing to redo")
            return None
        to_do = self.future.pop().invert()
        done = self._do(to_do)
        self.past.append(done)

        self.logger.info("Redid %s", done)

    def is_active(self, key, frame) -> bool:
        for _ in self.get_active(frame, key):
            return True
        return False

    def get_active(self, frame, key=None):
        keys = self.keys() if key is None else [key]

        for k in keys:
            for start, stop in self.start_stop_pairs(k):
                if start <= frame < stop:
                    yield k, (start, stop)

    def start_stop_pairs(self, key) -> Iterator[Tuple[int, int]]:
        starts = sorted(self.events[key.lower()], reverse=True)
        stops = sorted(self.events[key.upper()], reverse=True)

        if not (starts and stops):
            if starts:
                yield starts.pop(), Special.AFTER

            if stops:
                yield Special.BEFORE, stops.pop(0)

            for start in reversed(starts):
                self.logger.warning(
                    "Multiple starts and no stops for key '%s': ignoring start at frame %s",
                    key,
                    start,
                )

            for stop in reversed(stops):
                self.logger.warning(
                    "Multiple stops and no starts for key '%s': ignoring stop at frame %s",
                    key,
                    stop,
                )

            return

        # if stops[-1] < starts[-1]:
        #     yield Special.BEFORE, stops.pop()
        #
        # last = []
        #
        # if starts[0] > stops[0]:
        #     stops.insert(0, Special.AFTER)
        #
        # while True:
        #     start = starts.pop()
        #     stop = stops.pop()
        #
        #     if not starts:
        #         for stop in reversed(stops):
        #             self.logger.warning(
        #                 "Extra event stops for key '%s': ignoring at frame %s",
        #                 key, stop
        #             )
        #         return
        #     if not stops:
        #         for start in reversed(starts):
        #             self.logger.warning(
        #                 "Extra event starts"
        #             )

        early_stops = [] if starts else stops[::-1]
        if starts:
            while stops and stops[-1] < starts[-1]:
                early_stops.append(stops.pop())

        if early_stops:
            yield Special.BEFORE, early_stops.pop()

        while len(early_stops) > 1:
            self.logger.warning(
                "Multiple event stops before event start for key '%s': ignoring stop at frame %s",
                key,
                early_stops.pop(),
            )

        while starts and stops:
            start = starts.pop()
            stop = stops.pop()
            if stop <= start:
                self.logger.warning(
                    "Event stop before event start for key '%s': ignoring stop at frame %s",
                    key,
                    stop,
                )
                starts.append(start)
            else:
                yield start, stop

        for stop in reversed(stops):
            self.logger.warning(
                "Event stop before event start for key '%s': ignoring stop at frame %s",
                key,
                stop,
            )

        if starts:
            yield starts.pop(), Special.AFTER

        for start in reversed(starts):
            self.logger.warning(
                "Multiple event starts after last stop for key '%s': ignoring start at frame %s",
                key,
                start,
            )

    def to_df(self):
        rows = []
        for key in self.keys():
            for start, stop in self.start_stop_pairs(key):
                rows.append(
                    (start, stop, key, self.name(key), self.events[key].get(start, ""))
                )

        df = pd.DataFrame(
            sorted(rows), columns=["start", "stop", "key", "event", "note"]
        )

        for col, special in [("start", Special.BEFORE), ("stop", Special.AFTER)]:
            arr = pd.array(df[col], dtype=pd.Int64Dtype())
            arr[arr == special] = np.nan
            df[col] = arr

        return df

    def save(self, fpath=None, **kwargs):
        if fpath is None:
            self.logger.info("Printing to stdout")
            print(str(self))
        else:
            df = self.to_df()
            dump_results(df, fpath, **kwargs)
            self.changed = False
            self.logger.info("Saved to %s", fpath)

    def __str__(self):
        output = self.to_df()
        return df_to_str(output)

    @classmethod
    def from_df(cls, df: pd.DataFrame, key_mapping=None):
        el = EventLogger()
        for start, stop, key, event, note in df.itertuples(index=False):
            if event != key:
                el.key_mapping[key] = event

            if pd.isnull(start):
                if note:
                    start = Special.BEFORE.value
                    el.events[key][start] = note
            else:
                el.events[key][start] = note
            if stop:
                el.events[key.upper()][stop] = ""

        if key_mapping is not None:
            for k, v in key_mapping.items():
                existing = el.key_mapping.get(k)
                if existing is None:
                    el.key_mapping[k] = v
                elif existing != v:
                    raise ValueError(
                        "Given key mapping incompatible with given data. "
                        f"Key '{k}' has 2 different events ({v}, {existing})"
                    )
        return el

    @classmethod
    def from_csv(cls, fpath, key_mapping=None):
        df = load_results(fpath)
        return cls.from_df(df, key_mapping)
