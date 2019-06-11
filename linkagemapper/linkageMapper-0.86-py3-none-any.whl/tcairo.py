#!/usr/bin/env python
"""
Based on cairo-demo/X11/cairo-demo.c
"""

import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

SIZE = 12
import math

def triangle(ctx):
    ctx.move_to(SIZE, 0)
    ctx.rel_line_to(SIZE, 2 * SIZE)
    ctx.rel_line_to(-2 * SIZE, 0)
    ctx.close_path()


def square(ctx):
    ctx.move_to(0, 0)
    ctx.rel_line_to(2 * SIZE, 0)
    ctx.rel_line_to(0, 2 * SIZE)
    ctx.rel_line_to(-2 * SIZE, 0)
    ctx.close_path()


def bowtie(ctx):
    ctx.move_to(0, 0)
    ctx.rel_line_to(2 * SIZE, 2 * SIZE)
    ctx.rel_line_to(-2 * SIZE, 0)
    ctx.rel_line_to(2 * SIZE, -2 * SIZE)
    ctx.close_path()


def drawCircle(ctx, color=None):
    ctx.move_to(SIZE, SIZE)

    ctx.translate(SIZE, SIZE)
    ctx.new_path()
    ctx.arc(0, 0, SIZE, 0, 2 * math.pi)
    ctx.close_path()

    if color:
        ctx.set_source_rgb(*color)
        ctx.fill()

    ctx.move_to(0, 0)
    ctx.translate(-SIZE, -SIZE)


def draw(da, ctx):
    ctx.set_source_rgb(0, 0, 0)

    ctx.set_line_width(SIZE / 4)
    ctx.set_tolerance(0.1)

    # FIRST ROW;
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    ctx.save()
    ctx.new_path()

    ctx.translate(SIZE, SIZE)

    for k in range(6):
        ctx.new_path()
        drawCircle(ctx, (0, 0, 0))
        ctx.translate(3 * SIZE, 0)

    ctx.restore()


    """
    ctx.set_dash([], 0)
    draw_shapes(ctx, 0, 3 * SIZE, False)

    ctx.set_line_join(cairo.LINE_JOIN_BEVEL)
    stroke_shapes(ctx, 0, 6 * SIZE)

    ctx.set_line_join(cairo.LINE_JOIN_MITER)
    stroke_shapes(ctx, 0, 9 * SIZE)

    fill_shapes(ctx, 0, 12 * SIZE)

    ctx.set_line_join(cairo.LINE_JOIN_BEVEL)
    fill_shapes(ctx, 0, 15 * SIZE)
    ctx.set_source_rgb(1, 0, 0)
    stroke_shapes(ctx, 0, 15 * SIZE)
    """

def main():
    win = Gtk.Window()
    win.connect('destroy', lambda w: Gtk.main_quit())
    win.set_default_size(200, 40)

    drawingarea = Gtk.DrawingArea()

    drawingarea.set_size_request(200, 40)
    win.add(drawingarea)
    drawingarea.connect('draw', draw)

    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()

