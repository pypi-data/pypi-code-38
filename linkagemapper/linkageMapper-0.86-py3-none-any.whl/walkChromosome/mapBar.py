#!/bin/python

import cairo
import gi
gi.require_version("Gtk", '3.0')
from gi.repository import Gtk


class LocusMapBar(Gtk.DrawingArea):
    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        self.connect("draw", self.draw)
        self.set_size_request(200, 10)

        self.LocusNames = []
        self.Active = self.initActive()
        self.show_all()

    def initActive(self):
        return {
            "green": [],
            "red": [],
            "blue": []
        }

    def drawCircle(self, ctx, color=None):

        ctx.translate(self.circleSize, self.circleSize)

        ctx.new_path()
        ctx.arc(0, 0, self.circleSize, 0, 2 * 3.14)
        ctx.close_path()

        if color:
            ctx.set_source_rgba(*color, 1.0)
            ctx.fill()

        ctx.translate(-self.circleSize, -self.circleSize)

    def draw(self, da, ctx):
        # print("DRAWING %s" % self.Active)

        availableWidth = self.get_allocation().width

        Size = len(self.LocusNames)

        self.circleSize = max(min(availableWidth / (Size * 3), 12), 6)


        ctx.set_source_rgb(0, 0, 0)

        ctx.set_line_width(self.circleSize / 4)
        ctx.set_tolerance(0.1)

        # FIRST ROW;
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        ctx.save()
        ctx.new_path()

        ctx.translate(self.circleSize, self.circleSize)

        nb_rows = 1
        for k, locus in enumerate(self.LocusNames):
            color = (0, 0, 0)

            if k in self.Active["green"]:
                color = (0.1, 0.8, 0.1)
            elif k in self.Active["red"]:
                color = (0.8, 0.1, 0.1)
            elif k in self.Active["blue"]:
                color = (0.1, 0.1, 0.8)

            self.drawCircle(ctx, color)
            ctx.translate(3 * self.circleSize, 0)

            position_x = ctx.get_matrix()[4]

            if position_x > availableWidth:
                ctx.restore()
                ctx.save()
                ctx.translate(self.circleSize,
                              self.circleSize + 3 * self.circleSize * nb_rows)
                nb_rows += 1

        print(nb_rows)
        self.set_size_request(200, 4 * self.circleSize * nb_rows)
        ctx.restore()

    def loadData(self, alnData):
        self.LocusNames = list(alnData.MatchData["LocusName"])
        print(self.LocusNames)

