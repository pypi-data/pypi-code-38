class TextPos:
    def __init__(self, offset, col, line):
        assert offset >= -1
        self.offset = offset
        self.col = col
        self.line = line

    def new_line(self):
        return self.__class__((self.offset + 1) if self.offset >= 0 else -1, 0, self.line + 1)

    @classmethod
    def from_source(cls, src):
        lines = src.split('\n')
        return cls(len(src), len(lines[-1]), len(lines))

    def as_dict(self):
        return {
            'offset': self.offset,
            'col': self.col,
            'line': self.line
        }

    def __repr__(self):
        return self.__class__.__name__ + '({}, {}, {})'.format(self.offset, self.col, self.line)

    def __str__(self):
        return 'L{}C{}'.format(self.line, self.col)

    def __add__(self, num):
        if isinstance(num, int):
            return self.__class__((self.offset + num) if self.offset >= 0 else -1, self.col + num, self.line)
        elif isinstance(num, TextDeltaPos):
            return self.__class__((self.offset + num.offset) if self.offset >= 0 else -1,
                                  (self.col + num.col) if num.line == 0 else num.col,
                                  self.line + num.line)
        else:
            raise ValueError('Cannot add TextPos with {}'.format(num))

    def __radd__(self, num):
        return self + num

    def __sub__(self, other):
        assert self >= other
        return TextDeltaPos(
            self.offset - other.offset if self.offset >= 0 and other.offset >= 0 else -1,
            self.col - (other.col if self.line == other.line else 0),
            self.line - other.line
        )

    def __rsub__(self, other):
        return self - other

    def __gt__(self, other):
        assert isinstance(other, TextPos)
        if self.offset != -1 and other.offset != -1:
            return self.offset > other.offset
        else:
            return self.line > other.line or (self.line == other.line and self.col > other.col)

    def __ge__(self, other):
        assert isinstance(other, TextPos)
        if self.offset != -1 and other.offset != -1:
            return self.offset >= other.offset
        else:
            return self.line > other.line or (self.line == other.line and self.col >= other.col)

    def __lt__(self, other):
        assert isinstance(other, TextPos)
        return not (self >= other)

    def __le__(self, other):
        assert isinstance(other, TextPos)
        return not (self > other)

    def __eq__(self, other):
        assert isinstance(other, TextPos)
        return ((self.offset == other.offset
                 or self.offset == -1
                 or other.offset == -1)
                and self.line == other.line
                and self.col == other.col)


text_origin = TextPos.from_source('')


class TextDeltaPos(TextPos):
    @classmethod
    def from_source(cls, src):
        lines = src.split('\n')
        return cls(len(src), len(lines[-1]), len(lines) - 1)

    def __str__(self):
        if self.line == 0:
            return 'c+{}'.format(self.col)
        else:
            return 'l+{}C{}'.format(self.line, self.col)


class PosMap:
    pass


class ContiguousPosMap(PosMap):
    def __init__(self, src_start, src_end, dest_start, dest_end):
        self.src_start = src_start
        self.src_end = src_end
        self.dest_start = dest_start
        self.dest_end = dest_end

    def src_contains(self, pos):
        return self.src_start <= pos and self.src_end >= pos

    def dest_contains(self, pos):
        return self.dest_start <= pos and self.dest_end >= pos

    def src_rel(self, pos):
        if self.src_contains(pos):
            return 'in'
        elif pos < self.src_start:
            return 'before'
        else:
            return 'after'

    def dest_rel(self, pos):
        if self.dest_contains(pos):
            return 'in'
        elif pos < self.dest_start:
            return 'before'
        else:
            return 'after'


class IntervalOnTwoFilesError(Exception):
    pass


class RootPosMap(PosMap):
    def __init__(self, filename, maps):
        self.filename = filename
        self.src_start = 0
        if not hasattr(maps, '__iter__'):
            exit()
        self.maps = self.sort(maps)

    def sort(self, maps):
        return sorted(maps, key=lambda it: it.src_start)

    def find_file_root(self, filename):
        if self.filename == filename:
            return self
        else:
            for map in self.maps:
                if isinstance(map, RootPosMap):
                    found = map.find_file_root(filename)
                    if found:
                        return found
        return None

    def _for_file(self, filename):
        root = self.find_file_root(filename)
        if root is None:
            raise FileNotFoundError('There is no such file {} in the parsed tree.'.format(filename))
        return root._for_this()

    def _for_this(self):
        return (map for map in self.maps if not isinstance(map, RootPosMap))

    def _for_all(self):
        root_stack = [self]
        while root_stack:
            root = root_stack.pop()
            yield ('file', root.filename)
            for map in root.maps:
                if isinstance(map, RootPosMap):
                    root_stack.append(map)
                else:
                    yield ('map', map)

    def as_text(self):
        lines = []
        for t, obj in self._for_all():
            if t == 'file':
                lines.append('[{}]'.format(obj))
            else:
                lines.append('{}-{}={}-{}'.format(*obj))
        return '\n'.join(lines)

    def as_dict(self):
        d = {}
        fname = None
        for t, obj in self._for_all():
            if t == 'file':
                fname = obj
                d[fname] = []
            else:
                d[fname].append({
                    'src': (obj.src_start.as_dict(), obj.src_end.as_dict()),
                    'dest': (obj.dest_start.as_dict(), obj.dest_end.as_dict())
                })
        return d

    def src_to_dest_range(self, src_start, src_end, filename=None):
        before_start = self.src_to_dest(src_start, filename=filename)

        before_end, after_end = self.src_to_dest(
            src_end, filename=filename, return_pair=True
        )

        if after_end is None:
            end = before_end
        else:
            end = after_end

        if before_start > end:
            tmp = before_start
            before_start = end
            end = tmp

        return before_start, end

    def dest_to_src_range(self, dest_start, dest_end):
        filename_start, before_start = self.dest_to_src(dest_start)

        filename_end, before_end, after_end = self.dest_to_src(
            dest_end, return_pair=True
        )

        if after_end is None:
            end = before_end
        else:
            end = after_end

        if before_start > end:
            tmp = before_start
            before_start = end
            end = tmp

        if filename_end != filename_start:
            # vraiment pas cool !!
            raise IntervalOnTwoFilesError()

        return filename_start, before_start, end

    def src_to_dest(self, pos, filename=None, return_pair=False):
        if filename is None:
            seq = self._for_this()
        else:
            seq = self._for_file(filename)

        before = text_origin
        true_match = False
        for map in seq:
            rel = map.src_rel(pos)
            if rel == 'in':
                before = (map.dest_start + (pos - map.src_start))
                after = None
                true_match = True
                break
            elif rel == 'before':
                # pos is before obj so obj is after pos
                after = map.src_start
                break
            elif rel == 'after':
                # pos is after obj so obj is before pos
                before = map.src_end

        if return_pair:
            if true_match:
                return before, before
            else:
                return before, after
        else:
            return before

    def dest_to_src(self, pos, return_pair=False):
        before = text_origin
        true_match = False
        current_file = self.filename
        for t, obj in self._for_all():
            if t == 'file':
                current_file = obj
            else:
                rel = obj.dest_rel(pos)
                if rel == 'in':
                    before = (obj.src_start + (pos - obj.dest_start))
                    after = None
                    true_match = True
                    break
                elif rel == 'before':
                    # pos is before obj so obj is after pos
                    after = obj.src_start
                    break
                elif rel == 'after':
                    # pos is after obj so obj is before pos
                    before = obj.src_end

        if return_pair:
            if true_match:
                return current_file, before, before
            else:
                return current_file, before, after
        else:
            return current_file, before
