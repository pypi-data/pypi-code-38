# ---------------------------------------------------
# timeline elements in SVG
# ---------------------------------------------------
class Root:
    def __init__(self, theme, body, max_length_px, max_height_px, scale):
        self.node = theme.root % (max_length_px * scale, max_height_px * scale, max_length_px, max_height_px, body)
        self.theme = theme
        
class Axis:
    def __init__(self, theme, start_x_offset, end_x_offset):
        self.end_x_offset = end_x_offset
        self.start_x_offset = start_x_offset
        self.theme = theme

    def get_shape(self):
        y = 0
        t = self.theme.Arrow(-25, y, self.start_x_offset, self.end_x_offset)
        return t.node
    
    def get_height(self):
        return 20


class Marble:
    def __init__(self, theme, x_offset, y, text, coloring):
        self.theme = theme
        self.x_offset = x_offset
        self.color = coloring.get_color_for(text)
        self.text = text
        self.y = y

    def get_shape(self):
        c = self.theme.Circle(self.x_offset, self.y, self.text, self.color)
        return c.node
    
    def get_height(self):
        return 50

class Struct:
    def __init__(self, theme, x_offset, text, coloring, width, subitems, step_width):
        self.theme = theme
        self.x_offset = x_offset
        self.color = coloring.get_color_for(text)
        self.text = text
        self.width = width
        self.subitems = subitems
        self.step_width = step_width
        self.coloring = coloring
        self.height = self.step_width * len(self.subitems)
        self.shape = self.create_shape()

    def create_shape(self):
        y = 0
        c = self.theme.BlockWithText(self.x_offset, y, self.text, self.color, self.step_width, self.height)
        x_offset = self.x_offset
        y_offset = 3
        svg = ""
        for m in self.subitems:
            m = Marble(self.theme, x_offset, y_offset, m, self.coloring)
            svg += m.get_shape()
            y_offset += self.step_width
        return c.node + svg
    
    def get_shape(self):
        return self.shape
    
    def get_height(self):
        return self.height

class Terminate:
    def __init__(self, theme, x_offset):
        self.theme = theme
        self.x_offset = x_offset

    def get_shape(self):
        y = 0
        e = self.theme.End(self.x_offset, y)
        return e.node
    
    def get_height(self):
        return 50

class Error:
    def __init__(self, theme, x_offset):
        self.theme = theme
        self.x_offset = x_offset

    def get_shape(self):
        y = 0
        e = self.theme.Err(self.x_offset, y)
        return e.node

    def get_height(self):
        return 50

class OperatorBox:
    def __init__(self, theme, max_length_px, height, text):
        self.theme = theme
        self.max_length_px = max_length_px
        self.height = height
        self.text = text

    def get_shape(self):
        margin = 2
        y = 0
        box = self.theme.Block(0 + margin, y, self.max_length_px - 2 * margin, self.height, self.text, "white");
#         return self.theme.block % (0+margin,y,self.max_length_px-2*margin,self.height, self.max_length_px/2.0, y+self.height/2+5, self.text)
        return box.node

    def get_height(self):
        return 70
