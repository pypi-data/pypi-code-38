from .line import Line
from .block import Block, SizePref, Grid, safe_get,safe_set
from threading import Thread
import re

class InputBlock(Block):
    def __init__(self, name='input', grid=None, default_status=''):
        super().__init__(name,
                         text='> ',
                         hjust='<',
                         vjust='^',
                         grid=grid)
        # TODO when wrapping is supported, wrap this text
        self.w_sizepref = SizePref(hard_min='text', hard_max=float('inf'))
        self.h_sizepref = SizePref(hard_min=1, hard_max=1)  # both == 'text' if wrapping
        self.default_status = default_status
        self.status = self.default_status

    def display(self, width, height, x, y, term=None):
        prompt = '> '
        with self.write_lock:
            if term:
                with term.location(x=x, y=y):
                    if self.status:
                        line = Line(prompt + '{t.red}' + self.status, width, '<')
                        print(line.display.format(t=term), end='')
                    elif self.text:
                        line = prompt + self.text
                        print(line[:width] + (' ' * (width-len(line))), end='')
                    else:
                        line = Line(prompt + '{t.red}' + self.default_status, width, '<')
                        print(line.display.format(t=term), end='')
            else:
                return [line]  # for testing purposes only

class VFillBlock(Block):
    def __init__(self, text, name=None):
        border_text, seqs, last_seq = Line.parse(text)
        super().__init__(name=name,
                         text=text,
                         w_sizepref=SizePref(hard_min=len(border_text),
                                             hard_max=len(border_text)),
                         h_sizepref=SizePref(hard_min=0,
                                             hard_max=float('-inf')))

    def display(self, width, height, x, y, term=None):
        with self.write_lock:
            border_text, seqs, last_seq = Line.parse(self.text)
            out = []
            line = Line(self.text, width, '<')
            for h in range(height):
                if term:
                    with term.location(x=x, y=y+h):
                        print(line.display.format(t=term), end='')
                else:
                    out.append(line.display)
            if not term:
                return out
    @property
    @safe_get
    def text(self): return self._text

    @text.setter
    @safe_set
    def text(self, val):
        border_text, seqs, last_seq = Line.parse(val)
        Block.text.fset(self, val)
        Block.w_sizepref.fset(self, SizePref(hard_min=len(border_text), hard_max=len(border_text)))


class HFillBlock(Block):
    def __init__(self, text, name=None):
        zero_or_one = 0 if not text else 1  # Don't take up space if there's no text
        # TODO test the -inf and remove w_max
        w_max = "text" if text else 0  # But if there is space, fill the entire width of the block 
        super().__init__(name=name,
                         text=text,
                         w_sizepref=SizePref(hard_min=zero_or_one, hard_max=float('-inf')),
                         h_sizepref=SizePref(hard_min=zero_or_one, hard_max=zero_or_one)
        )

    def display(self, width, height, x, y, term=None):
        if not self.text:
            if not term:
                return []
            return

        with self.write_lock:
            text = Line.repeat_to_width(self.text, width).display
            if term:
                with term.location(x=x, y=y):
                    print(text.format(t=term), end='')
            else:
                return [text]  # for testing purposes only

    @property
    @safe_get
    def text(self): return self._text

    @text.setter
    @safe_set
    def text(self, val):
        zero_or_one = 0 if not val else 1  # Don't take up space if there's no text
        Block.text.fset(self, val)
        Block.w_sizepref.fset(self, SizePref(hard_min=zero_or_one, hard_max=float('-inf')))
        Block.h_sizepref.fset(self, SizePref(hard_min=zero_or_one, hard_max=zero_or_one))

class BareBlock(Block):
    def __init__(self,
                 name=None,
                 text=None,
                 hjust='<',  # horizontally left-justified within block
                 vjust='^',  # vertically centered within block
                 block_just=True,  # justify block as a whole vs line-by-line
                 # The SizePrefs indicate how much screen real estate (width and height) this
                 # block desires/requires when displayed. Here, we default the block to
                 # as-much-as-you-got-but-none-is-fine.
                 w_sizepref = SizePref(hard_min=0, hard_max=float('inf')),
                 h_sizepref = SizePref(hard_min=0, hard_max=float('inf')),
                 grid=None):
        super().__init__(name=name, text=text, hjust=hjust, vjust=vjust, block_just=block_just,
                         w_sizepref=w_sizepref, h_sizepref=h_sizepref, grid=grid)
        self._prev_seq = '{t.normal}'

    def display(self, width, height, x, y, term=None):
        with self.write_lock:
            out = []
            if self.text is not None and len(self.text) != 0:
                available_for_text_rows = max(0, height)
                available_for_text_cols = max(0, width)

                all_btext_rows = []
                for row in self.text.split('\n'):
                    all_btext_rows.append(row)  # TODO all we really need is a count here, right?
                useable_btext_rows = all_btext_rows[:available_for_text_rows]

                # Calculate the values for adjusting the text vertically within the block
                # if there's extra empty rows.
                ver_pad = max(0, (available_for_text_rows - len(all_btext_rows)))
                top_ver_pad = 0
                if self.vjust == '=':
                    top_ver_pad = ver_pad // 2
                elif self.vjust == 'v':
                    top_ver_pad = ver_pad

                # Finally, build the block from top to bottom, adding each next line
                # if there's room for it. The bottom gets cut off if there's not enough room.
                # This behavior (cutting from the bottom) is not configurable.
                line = None
                remaining_rows = height

                # By default, empty rows fill out the bottom of the block.
                # Here we move some of them up above the text if we need to.
                ver_pad_count = top_ver_pad
                while ver_pad_count and remaining_rows:
                    line = Line(' ' * width, width, self.hjust)
                    out.append(line)
                    ver_pad_count -= 1
                    remaining_rows -= 1

                # This is the main text of the block
                prev_seq = '{t.normal}'                
                for i in range(max(0,available_for_text_rows - top_ver_pad)):
                    if remaining_rows <= 0:
                        break
                    line = None
                    if i >= len(useable_btext_rows):
                        line = Line(prev_seq + ' ', width, self.hjust)
                    else:
                        line = Line(prev_seq + useable_btext_rows[i], width, self.hjust)
                    if line:
                        out.append(line)
                        prev_seq = line.last_seq
                        remaining_rows -= 1

            if len(out):
                out[-1].display += '{t.normal}'

            if term:
                for j, line in enumerate(out):
                    with term.location(x=x, y=y+j):
                        # Can debug here by printing to a file
                        #with open('/tmp/bare', 'a') as f:
                        #    f.write(line.display + '\n')
                            
                        try:
                            text = re.sub(r"\r?\n?$", "", line.display, 1)
                            print(text.format(t=term), end='')
                        except ValueError:
                            raise ValueError(line.rstrip())
                term.move(term.height, term.width)  # TODO This doesn't work
            else:
                return [line.display for line in out]  # for testing purposes only

class FramedBlock(Block):
    LEFT_BORDER, TOP_BORDER, TITLE, TITLE_SEP, TEXT, BOTTOM_BORDER, RIGHT_BORDER = 1,2,3,4,5,6,7
    layout = [1,(2,3,4,5,6),7]
    def __init__(self,
                 block,
                 name=None,
                 text=' ',  # TODO
                 no_borders=False,
                 top_border=Block.MIDDLE_DOT,
                 bottom_border=Block.MIDDLE_DOT,
                 left_border=Block.MIDDLE_DOT,
                 right_border=Block.MIDDLE_DOT,
                 title = '',
                 title_sep = ''):

        top_border = None if no_borders and top_border == Block.MIDDLE_DOT else top_border
        bottom_border = None if no_borders and bottom_border == Block.MIDDLE_DOT else bottom_border
        left_border = None if no_borders and left_border == Block.MIDDLE_DOT else left_border
        right_border = None if no_borders and right_border == Block.MIDDLE_DOT else right_border

        self._blocks = {}

        self._blocks[1] = VFillBlock(left_border)
        self._blocks[2] = HFillBlock(top_border)
        self._blocks[3] = BareBlock(text=title, hjust='^', vjust='^',
                                   h_sizepref = SizePref(hard_min=1, hard_max=1))
        self._blocks[4] = HFillBlock(title_sep)
        self._blocks[5] = block
        self._blocks[6] = HFillBlock(bottom_border)
        self._blocks[7] = VFillBlock(right_border)

        super().__init__(name=name,
                         text=text,
                         hjust='^',
                         vjust='^',
                         block_just=True,
                         grid = Grid(FramedBlock.layout, self._blocks))

        self.no_borders = no_borders

    @property
    @safe_get
    def text(self): return self._blocks[5].text

    @text.setter
    @safe_set
    def text(self, val):
        self._blocks[5].text = val

    @property
    @safe_get
    def no_borders(self): return self._no_borders

    @no_borders.setter
    @safe_set
    def no_borders(self, val):
        self._no_borders = val

    @property
    @safe_get
    def top_border(self): return self._top_border

    @top_border.setter
    @safe_set
    def top_border(self, val):
        self._top_border = val
        top_border = None if self.no_borders and self.top_border == Block.MIDDLE_DOT else val
        self._blocks[FramedBlock.TOP_BORDER].text = top_border

    @property
    @safe_get
    def bottom_border(self): return self._bottom_border

    @bottom_border.setter
    @safe_set
    def bottom_border(self, val):
        self._bottom_border = val
        bottom_border = None if self.no_borders and self.bottom_border == Block.MIDDLE_DOT else val
        self._blocks[FramedBlock.BOTTOM_BORDER].text = val

    @property
    @safe_get
    def left_border(self): return self._left_border

    @left_border.setter
    @safe_set
    def left_border(self, val):
        self._left_border = val
        self._blocks[FramedBlock.LEFT_BORDER].text = val

    @property
    @safe_get
    def right_border(self): return self._right_border

    @right_border.setter
    @safe_set
    def right_border(self, val):
        self._right_border = val
        self._blocks[FramedBlock.RIGHT_BORDER].text = val

    @property
    @safe_get
    def title(self): return self._title

    @title.setter
    @safe_set
    def title(self, val):
        self._title = val
        self._blocks[FramedBlock.TITLE].text = val

    @property
    @safe_get
    def title_sep(self): return self._title_sep

    @title_sep.setter
    @safe_set
    def title_sep(self, val):
        self._title_sep = val
        self._blocks[FramedBlock.TITLE_SEP].text = val

    def display(self, width, height, x, y, term=None):
        raise NotImplementedError("Blocks with grids don't implement display method")
