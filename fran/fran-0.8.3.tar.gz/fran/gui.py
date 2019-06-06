#!/usr/bin/env python
import json
import sys
import os
from functools import wraps
from tkinter import filedialog, simpledialog, messagebox
from typing import Tuple, Optional, Callable
import logging
from string import ascii_letters
import contextlib
import tkinter as tk
import datetime as dt

import numpy as np
import pandas as pd

from fran import __version__
from fran.common import Special
from fran.constants import (
    DEFAULT_CACHE_SIZE,
    DEFAULT_FPS,
    DEFAULT_THREADS,
    DEFAULT_FLIPX,
    DEFAULT_FLIPY,
    DEFAULT_ROTATE,
    CONTROLS,
    DEFAULT_KEYS,
    FRAME_LEVEL,
)
from fran.events import EventLogger
from fran.frames import FrameSpooler, ImageConverter

with contextlib.redirect_stdout(None):
    import pygame


logger = logging.getLogger(__name__)

LETTERS = set(ascii_letters)


def noop(arg):
    return arg


class Window:
    def __init__(
        self,
        spooler: FrameSpooler,
        fps=DEFAULT_FPS,
        key_mapping=None,
        out_path=None,
        flipx=False,
        flipy=False,
        rotate=0,
    ):
        self.logger = logger.getChild(type(self).__name__)

        self.spooler = spooler
        self.im_conv = ImageConverter(self.spooler.frame_dtype)
        self.fps = fps
        self.out_path = out_path

        pygame.init()
        self.clock = pygame.time.Clock()
        first = self.spooler.current.result()
        self.im_surf: pygame.Surface = pygame.surfarray.make_surface(
            self.im_conv(first).T
        )
        self.im_surf.set_palette([(idx, idx, idx) for idx in range(256)])
        self.transformed_surf: Callable[[], pygame.Surface] = self._make_surf(
            flipx, flipy, rotate
        )
        width, height = self.transformed_surf().get_size()
        self.screen = pygame.display.set_mode((width, height))
        self._blit()
        pygame.display.update()

        if out_path and os.path.exists(out_path):
            self.events = EventLogger.from_csv(out_path, key_mapping)
        else:
            self.events = EventLogger(key_mapping)

        self.update_caption()

    def update_caption(self, msg=None):
        if msg is None:
            msg = "frame{}({:.0f}%)|contrast({:.02f},{:.02f})|{:.0f}fps".format(
                self.spooler.current_idx,
                self.spooler.current_idx / self.spooler.frame_count * 100,
                self.im_conv.contrast_lower.idx / 100,
                self.im_conv.contrast_upper.idx / 100,
                self.clock.get_fps(),
            )
        pygame.display.set_caption("fran|" + msg)

    def _make_surf(self, flipx=False, flipy=False, rotate=0):
        def fn():
            surf = self.im_surf
            if flipx or flipy:
                surf = pygame.transform.flip(surf, flipx, flipy)
            if rotate % 360:
                surf = pygame.transform.rotate(surf, rotate)
            return surf

        return fn

    def _blit(self):
        self.screen.blit(self.transformed_surf(), (0, 0))

    def step(self, step=0, force_update=False):
        if step or force_update:
            arr = self.spooler.step(step).result()

            self.draw_array(arr)
            self.update_caption()

        self.clock.tick(self.fps)

    def active_events(self):
        yield from self.events.get_active(self.spooler.current_idx)

    def _handle_step_right(self):
        self.logger.log(FRAME_LEVEL, "Step Right detected")
        return 1, True

    def _handle_step_left(self):
        self.logger.log(FRAME_LEVEL, "Step Left detected")
        return -1, True

    def handle_events(self) -> Tuple[Optional[int], bool]:
        """
        Hold arrow: 1 in that direction
        Hold shift+arrow: 10 in that direction
        Press Ctrl+arrow: 1 in that direction
        Enter: print results
        lower-case letter: log event initiation / cancel event termination
        upper-case letter: log event termination / cancel event initiation

        :return:
        """
        while pygame.event.peek():
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.logger.log(FRAME_LEVEL, "Quit detected")
                return None, False
            if event.type == pygame.KEYDOWN:
                if event.mod & pygame.KMOD_CTRL:
                    if event.key == pygame.K_s:  # save
                        self.save()
                    elif event.key == pygame.K_h:  # help
                        self.print("\n" + CONTROLS + "\n")
                    elif event.key == pygame.K_z:  # undo
                        self.events.undo()
                    elif event.key == pygame.K_r:  # redo
                        self.events.redo()
                    elif event.key == pygame.K_n:  # note
                        self._handle_note()
                    elif event.key == pygame.K_d:  # dump event JSON
                        self._dump_events()
                elif event.key == pygame.K_PERIOD:  # aka ">" step right
                    return self._handle_step_right()
                elif event.key == pygame.K_COMMA:  # aka "<" step left
                    return self._handle_step_left()
                elif event.unicode in LETTERS:  # log event
                    self.events.insert(event.unicode, self.spooler.current_idx)
                elif event.key == pygame.K_RETURN:  # show results
                    df = self.results(True)
                    self.print(df)
                elif event.key == pygame.K_SPACE:  # show active events
                    self.print(
                        f"Active events @ frame {self.spooler.current_idx}:\n\t{self.get_actives_str()}"
                    )
                elif event.key == pygame.K_BACKSPACE:  # show frame info
                    self.show_frame_info()
                elif event.key == pygame.K_DELETE:  # delete a current event
                    if event.mod & pygame.KMOD_SHIFT:
                        self._handle_delete_single()
                    else:
                        self._handle_delete()
        else:
            pressed = pygame.key.get_pressed()
            speed = 10 if pressed[pygame.K_LSHIFT] else 1

            if pressed[pygame.K_RIGHT]:
                return speed, True
            if pressed[pygame.K_LEFT]:
                return -speed, True

            if self._handle_contrast(pressed):
                return 0, True

        return 0, False

    def show_frame_info(self, frame=None, contrast_lower=None, contrast_upper=None):
        if frame is None:
            frame = self.spooler.current_idx
        if contrast_lower is None:
            contrast_lower = self.im_conv.contrast_lower.idx / 100
        if contrast_upper is None:
            contrast_upper = self.im_conv.contrast_upper.idx / 100
        self.print(
            f"Frame {frame}, "
            f"contrast = ({contrast_lower:.02f}, {contrast_upper:.02f})"
        )

    def _select_in_progress_event(self, title="Select event", auto=True):
        self.update_caption("see event prompt")
        self.logger.info("Selecting in-progress event")
        actives = sorted(self.active_events())
        if not actives:
            self.print("No events in progress")
        elif len(actives) == 1 and auto:
            k, (start, stop) = actives[0]
            self.print(f"\tAutomatically selecting only event, {k}: {start} -> {stop}")
            return k, (start, stop)
        else:
            prefix = "In-progress events:"
            actives_str = "\n\t".join(
                self.fmt_key_startstop(k_startstop) for k_startstop in actives
            )
            suffix = "Type which event to select:"

            msg = f"{prefix}\n\n\t{actives_str}\n\n{suffix}"

            key = simpledialog.askstring(title, msg) or ""
            key = key.strip().lower()
            if key:
                actives_d = dict(actives)
                if key in actives_d:
                    return key, actives_d[key]
                else:
                    self.print(f"Event '{key}' not in progress")

        return None

    def _handle_note(self):
        selection = self._select_in_progress_event("Edit note")
        if selection:
            key, (start, stop) = selection
            initial = self.events.events[key].get(start, "")
            self.update_caption("see note prompt")
            note = simpledialog.askstring(
                "Edit note",
                f'Enter note for event "{self.events.name(key)}" ({start} -> {stop}):',
                initialvalue=initial,
            )
            if note is not None:
                self.events.insert(key, start or 0, note.strip())
                self.update_caption("edited note")
                return
        self.update_caption("note edit cancelled")

    def _handle_delete_single(self):
        self.update_caption("see key prompt")
        self.logger.info("Selecting key on this frame")
        keys = []
        for k, d in self.events.events.items():
            if self.spooler.current_idx in d:
                keys.append(k)
        if not keys:
            self.print("\tNo keys pressed on this frame")
            return

        msg = "Pressed keys:\n\t" + "\n\t".join(
            f"{key} ('{self.events.key_mapping.get(key.lower(), key.lower())}')"
            for key in keys
        )
        key = simpledialog.askstring("Select keypress", msg) or ""

        if key:
            if key in keys:
                self.events.delete(key, self.spooler.current_idx)
                self.update_caption("keypress deleted")
                return
            else:
                self.print(f"Key '{key}' not pressed at this frame")

        self.update_caption("keypress delete cancelled")

    def _handle_delete(self):
        selection = self._select_in_progress_event("Delete event", False)
        if selection:
            key, (start, stop) = selection
            self.update_caption("see confirmation")
            if messagebox.askyesno(
                f"Delete event",
                f'Deleting event "{self.events.name(key)}" ({start} -> {stop}).\n\nAre you sure?',
            ):
                self.events.delete(key, start)
                self.events.delete(key.upper(), stop)
                self.update_caption("deleted")
                return
        self.update_caption("delete cancelled")

    def fmt_key_startstop(self, key_startstop):
        key, (start, stop) = key_startstop
        name = self.events.name(key)
        name_str = f' ("{name}")' if name == key.lower() else ""
        if start == Special.BEFORE:
            start = "BEFORE"
        if stop == Special.AFTER:
            stop = "AFTER"
        return f"{key}{name_str} [{start} --> {stop}]"

    def get_actives_str(self):
        actives = sorted(self.active_events())
        return "\n\t".join(
            self.fmt_key_startstop(k_startstop) for k_startstop in actives
        )

    def input(self, msg):
        self.print(msg, end="")
        return input().strip()

    def _handle_contrast(self, pressed):
        mods = pygame.key.get_mods()
        if pressed[pygame.K_UP]:
            if mods & pygame.KMOD_SHIFT:
                self.im_conv.contrast_upper.increase()
            else:
                self.im_conv.contrast_lower.increase()
            return True
        elif pressed[pygame.K_DOWN]:
            if mods & pygame.KMOD_SHIFT:
                self.im_conv.contrast_upper.decrease()
            else:
                self.im_conv.contrast_lower.decrease()
            return True
        return False

    @wraps(print)
    def print(self, *args, **kwargs):
        print_kwargs = {"file": sys.stderr, "flush": True}
        print_kwargs.update(**kwargs)
        print(*args, **print_kwargs)

    def results(self, with_lengths=False):
        df = self.events.to_df()
        if with_lengths:
            out_of_bounds = pd.isnull(df.start)
            starts = df.start.copy()
            starts[pd.isnull(starts)] = 0

            out_of_bounds = np.logical_or(out_of_bounds, pd.isnull(df.stop))
            stops = df.stop.copy()
            stops[pd.isnull(stops)] = self.spooler.frame_count

            lengths = stops - starts
            lengths = [
                f"{'>' if is_oob else ''}{length}"
                for length, is_oob in zip(lengths, out_of_bounds)
            ]

            df.insert(2, "length", lengths)
        return df

    def save(self, fpath=None, ask=True):
        fpath = fpath or self.out_path
        if ask and not fpath:
            self.update_caption("see file prompt")
            fpath = filedialog.asksaveasfilename(
                filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
            )

        if not fpath:
            fpath = None

        self.events.save(fpath)
        if fpath:
            self.update_caption("saved")
        else:
            self.update_caption()

    def draw_array(self, arr):
        pygame.surfarray.blit_array(self.im_surf, self.im_conv(arr).T)
        self.screen.blit(self.transformed_surf(), (0, 0))

        pygame.display.update()

    def loop(self):
        while True:
            step_or_none, should_update = self.handle_events()
            if step_or_none is None:
                break
            self.step(step_or_none, should_update)

        return self.results()

    def close(self):
        self.spooler.close()
        pygame.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _dump_events(self):
        self.update_caption("see file prompt")

        d = self.events.to_dict()
        s = json.dumps(d, indent=2, sort_keys=False)

        fpath = filedialog.asksaveasfilename(
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )

        if fpath:
            with open(fpath, "w") as f:
                f.write(s)

        self.print(s)
        self.update_caption("dumped events for debug")


def run(
    fpath,
    out_path=None,
    cache_size=DEFAULT_CACHE_SIZE,
    max_fps=DEFAULT_FPS,
    threads=DEFAULT_THREADS,
    keys=DEFAULT_KEYS.copy(),
    flipx=DEFAULT_FLIPX,
    flipy=DEFAULT_FLIPY,
    rotate=DEFAULT_ROTATE,
):
    logger.info("Starting fran v%s", __version__)
    logger.info(
        "Timestamp: %s", dt.datetime.now(dt.timezone.utc).astimezone().isoformat()
    )
    logger.debug("Input file: %s", fpath)
    logger.debug("Output file: %s", out_path)
    logger.debug("Max FPS: %s", max_fps)
    logger.debug("Threads: %s", threads)
    logger.debug("Event names: %s", keys)
    logger.debug("Flip X: %s", flipx)
    logger.debug("Flip Y: %s", flipy)
    logger.debug("Rotate: %s", rotate)

    tk_root = tk.Tk()
    tk_root.withdraw()

    if not fpath:
        fpath = filedialog.askopenfilename(
            filetypes=(("TIFF files", "*.tif *.tiff"), ("All files", "*.*"))
        )
        if not fpath:
            logger.warning("No path given, exiting")
            return 0
    spooler = FrameSpooler(fpath, cache_size, max_workers=threads)
    with Window(spooler, max_fps, keys, out_path, flipx, flipy, rotate) as w:
        w.loop()
        if w.events.changed:
            w.save()
        else:
            logger.info("No changes since last save")
        logger.info("Exiting...")
    logger.info("Exited!")

    return 0
