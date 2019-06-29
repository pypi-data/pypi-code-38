from __future__ import print_function
from pyparsing import *
from .svgshapes import *
import sys
import argparse
import math
import importlib

start_character = "+"
nop_event_character = '-'
completion_symbol = "|"
error_character = "#"
infinity_character = ">"

colon = Suppress(":")
comment_start = "//"
nop_event = Word(nop_event_character, exact=1)
# our marble can be either single alphanumeric character, or multiple characters surrounded by ()
marble_text = alphanums
start_symbol = Suppress(start_character)
simple_marble = Word(marble_text, exact=1)
bracked_marble = Suppress("(") + Word(alphanums + "'\"._-") + Suppress(")")
groupped_marble = Combine("{" + Word(marble_text + ",") + "}")
marble = Or([simple_marble, bracked_marble , groupped_marble])
end = Or([completion_symbol, error_character, infinity_character]).setResultsName('end')
timeline_name = Or([QuotedString(quoteChar='"'), Word(alphanums + ",./<>?;'\"[]\{}|`~!@#$%^&*()-=_+")]).setResultsName('name')
source_keyword = "source"
operator_keyword = "operator"
event = Or([nop_event, marble])
events = Group(ZeroOrMore(event)).setResultsName('events')
padding = Optional(Word('.')).setResultsName('padding')
events_sequence = Group(padding + start_symbol + events + end).setResultsName('events_sequence', True)
skewed_group = Suppress("{") + OneOrMore(events_sequence) + Suppress("}")
type = Or([source_keyword, operator_keyword]).setResultsName('type')
source_or_operator = Group(type + timeline_name + colon + Or([events_sequence, skewed_group]))

marble_diagram_keyword = "marble"
marble_diagram_body = OneOrMore(source_or_operator)
marble_diagram_name = Word(alphanums + "_").setResultsName("diagram_name")
marble_diagram = Group(Suppress(marble_diagram_keyword) + marble_diagram_name + Suppress("{") + marble_diagram_body + Suppress("}"))
marble_diagrams = OneOrMore(marble_diagram)
marble_diagrams.ignore(comment_start + restOfLine)

class Timeline:
    def __init__(self, parsed_list, theme):
        self.theme = theme
        self.type = parsed_list.type
        self.name = parsed_list.name
        self.timelines = parsed_list.events_sequence
        self.rotation_deg = 0
        if len(self.timelines) > 1:
            self.rotation_deg = 15
        max_index = max(map(lambda x: 2 + len(x.events) + len(x.padding), self.timelines))
        # this is used as distance on flat axis between two time events
        self.base_thick_width = 50.0
        # this is used as distance on skewed between two time events
        self.tick_width = self.base_thick_width / math.cos(self.rotation_deg * math.pi / 180.0)
        
        self.width = self.tick_width * max_index
        self.top_margin = 30
        self.total_height = 0
        
    def create_groupped_symbol(self, o, x_offset, coloring):
        # Sub-parsing groupped marble
        ungroupped_marble = Suppress("{") + Word(marble_text) + ZeroOrMore(Suppress(",") + Word(marble_text)) + Suppress("}")
        subitems = ungroupped_marble.parseString(o)
        step_width = 1.0 * self.base_thick_width
        body = ", ".join(map(lambda x: str(x), subitems))
        width = step_width * len(subitems)
        groupped_symbol = Struct(self.theme, x_offset, body, coloring, width, subitems, step_width)
        return groupped_symbol
        
    def __get_timeline_shapes(self, coloring, timeline_items):
        # adding events
        theme = self.theme
        self.end = timeline_items.end
        x_offset = 0
        global parseString
        for o in timeline_items.events:
            if o.startswith('{') and o.endswith('}'):
                groupped_symbol = self.create_groupped_symbol(o, x_offset, coloring)
                self.symbols.append(groupped_symbol)
            elif o != nop_event_character:
                self.symbols.append(Marble(theme, x_offset, 0, o, coloring))
            x_offset += self.tick_width

        # adding completion, error or infinity_character symbol to the axis 
        if self.end == completion_symbol:
            self.symbols.append(Terminate(theme, x_offset))
        elif self.end == error_character:
            self.symbols.append(Error(theme, x_offset))

        # adding time axis
        self.symbols.insert(0, Axis(theme, 0, x_offset + 2 * self.base_thick_width))

    def get_svg(self, y, coloring, max_length):
        svg = ""
        yy = y + self.top_margin
        for timeline_items in self.timelines: 
            self.symbols = []
            self.__get_timeline_shapes(coloring, timeline_items)
            x_offset = self.base_thick_width * len(timeline_items.padding)
            g_id = self.type + "_" + self.name
            rot_yy = yy
            svg += '<g id="%s" transform="rotate(%s %s %s) translate(%s,%s)">' % (g_id, self.rotation_deg, x_offset, rot_yy , x_offset, yy)
            for obj in self.symbols:
                svg += obj.get_shape()
                h = obj.get_height()
                if self.total_height < h + self.top_margin :
                    self.total_height = h + self.top_margin 
            svg += '</g>'
            
        # and finally - inserting an extra axis - only when we are in the skewed block mode
        if len(self.timelines) > 1:
            max_padding = max(map(lambda x: len(x.padding), self.timelines))
            a = Axis(self.theme, 0, self.base_thick_width * (4 + max_padding))
            axisSvg = '<g id="skew" transform="translate(0 %s)">%s</g>' % (yy, a.get_shape())
            svg = axisSvg + svg
        return svg

    def height(self):
        "returns height in pixels. This must be called after get_svg()"
        
        # let's calculate all bounding boxes
        max_height = 0
        for events_sequence in self.timelines:
            timeline_width = self.base_thick_width * (1 + len(events_sequence.events))
            timeline_height = self.total_height
            bb = (timeline_width, timeline_height)
            # width of the diagonal
            diag = math.sqrt(bb[0] * bb[0] + bb[1] * bb[1])
            alpha_rad = math.atan2(bb[1], bb[0])
            alpha_deg = alpha_rad * 180.0 / math.pi
            # after rotation
            beta_deg = alpha_deg + self.rotation_deg
            beta_rad = beta_deg * math.pi / 180.0 
            height = diag * math.sin(beta_rad)
            if max_height < height:
                max_height = height 
        return max_height

class Source(Timeline):
    def __init__(self, parsed_list, theme):
        Timeline.__init__(self, parsed_list, theme)

class Operator:
    def __init__(self, parsed_list, theme):
        self.theme = theme
        self.timeline = Timeline(parsed_list, theme)
        self.name = parsed_list.name
        self.width = self.timeline.width
        self.box_height = 80
        self.top_margin = 10

    def height(self):
        "height in pixels"
        return self.box_height + self.timeline.height() + 2 * self.top_margin

    def get_svg(self, y, coloring, max_length):
        theme = self.theme
        box_y = y + self.top_margin
        box = OperatorBox(theme, max_length, self.box_height, self.name)
        svg = '<g transform="translate(0 %s)">' % box_y
        svg += box.get_shape() + self.timeline.get_svg(0 + self.box_height + self.top_margin, coloring, max_length)
        svg += '</g>'
        return svg

# ---------------------------------------------------
# events_sequence elements
# ---------------------------------------------------

def get_objects(parse_result, theme):
    global source_keyword
    global operator_keyword
    result = []
    for line in parse_result:
        type = line[0]
        if type == operator_keyword:
            t = Operator(line, theme)
        elif type == source_keyword:
            t = Source(line, theme)
        else:
            raise Exception("unsupported type")
        result.append(t)
    return result

# other colouring schemes can be added here
palettes = {'default': ["#ffcc00", "#48b3cd", "#ffaacc", "#e5ff7c", "#ececec", "#a4ecff", "#ff6600", "#a0c800", "#ff3a3a", "#afafe9", "#db7c7c", "#80ffe6"]}

class Coloring:
    'This object is stateful color provider for each of the marble'
    
    def __init__(self, paletteName='default'):
        global palettes
        self.color_palette = palettes[paletteName]
        self.colormap = {}
        self.index = 0

    def get_color_for(self, marbleId):
        if not marbleId in self.colormap:
            self.colormap[marbleId] = self.color_palette[self.index]
            self.index += 1
            if self.index >= len(self.color_palette):
                self.index = 0
        return self.colormap[marbleId]

class SvgDocument:
    def __init__(self, row_objects, theme, scale):
        self.theme = theme
        self.scale = scale
        self.coloring = Coloring()
        self.row_objects = row_objects
        # in pixels
        self.max_row_width = max(map(lambda row: row.width, self.row_objects))

    def get_document(self):
        theme = self.theme
        scale = self.scale
        body = ""
        y = 0
        for row in self.row_objects:
            body += row.get_svg(y, self.coloring, self.max_row_width)
            y = y + row.height()

        r = Root(theme, body, self.max_row_width, y, scale / 100.0)
        return r.node

