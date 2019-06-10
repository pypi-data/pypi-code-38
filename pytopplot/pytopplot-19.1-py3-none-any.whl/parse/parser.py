import numpy as np
import re


class ABCIDATA:
    """Object of parsed .top plot data
    Since the .top file format is statefull, so is this object.
    On top of this, each plot may contain more then one plot whit its own plot style.
    So this object may seems ridiculous. Because it is.

    When new data is added to the object, it is added to the buffer.
    New data, legends, title and so on may be added to buffer.
    When new plot is requested, buffer gets flushed. Flushed data is immutable

    Object itself contains plot data, stored in self._data dict. Dict keys are line styles (dotted, dashed etc).
    Each dict value is a list of data chunks. They are split in chunks because they are not supposed to be connected with lines
    Title, xlab, ylab, legends are pretty self explanatory. self.__desc["else"] is everything else that was on the plot."""

    ALLOCATE_SIZE = 10000  # numpy default buffer allocation size

    def __init__(self):
        self.__buffer_flush = (
            True
        )  # flag indicating if the new buffer should be created
        self.__data = {}  # dict of buffers of type {key:[chunk1, chunk2, ...], }.
        # Buffer keys are named after line stiles: "dotted" "dashed" "dashdot" "solid"
        # Data is stored in chunks because it is unclear when and why it is done this way in .top files
        # This is awful and should be refactored
        self.__reverse = False  # indicates if X-Y order is reversed
        self.__desc = {
            "title": "",
            "xlab": "",
            "ylab": "",
            "else": [],
        }  # plot title, labels and other optional info
        self.__last_desc = "title"  # key of the last used self.__desc
        self.__store_to_new = False
        self.__last_data_name = ""  # key of the last used self.__data
        self.__last_data_index = 0  # pointer to the last position
        self.__legends = {}  # plot legends
        self.__pattern = re.compile(
            r"(X+|V+|F)"
        )  # precompiled pattern to find and replace sub/superscripts in strings

    def __buffer_allocate(self, n=ALLOCATE_SIZE):
        """Allocate new buffer"""
        self.__buffer = np.zeros((n, 2))
        self.__buffer_pos = 0

    def __buffer_crop(self):
        """Crop buffer to the last used position"""
        self.__buffer.resize((self.__buffer_pos, 2))

    def store_to_new(self, val):
        """Set store_to_new flag"""
        self.__store_to_new = val

    def insert(self, x, y):
        """Append coordinates to buffer"""
        if self.__buffer_flush:
            self.__buffer_allocate()
            self.__buffer_flush = False
        if len(self.__buffer) == self.__buffer_pos:
            self.__buffer.resize((self.__buffer_pos * 10, 2))
        self.__buffer[self.__buffer_pos] = [x, y]
        self.__buffer_pos += 1

    def buffer_dump(self):
        """Return current buffer"""
        self.__buffer_crop()
        return self.__buffer

    def buffer_store(self, name, new):
        """Store current buffer with key "name".
        If "new" is set to True, or store_to_new flag is raised, data will be sent to new chunk"""
        self.__buffer_crop()
        self.__last_data_name = name
        if name in self.__data:
            if self.__store_to_new or new:
                self.__data[name].append(self.__buffer)
                self.store_to_new(False)
                self.__last_data_index = len(self.__data[name]) - 1
            else:
                self.__data[name][0] = np.concatenate(
                    (self.__data[name][0], self.__buffer)
                )
                self.__last_data_index = 0
        else:
            self.__data[name] = [self.__buffer]
            self.__last_data_index = 0
        self.__buffer_flush = True

    def last_is_legend(self, text):
        """Last N coordinate entries are actually a legend line"""
        self.__legends[self.__last_data_name] = text
        self.__data[self.__last_data_name].pop(self.__last_data_index)

    def legends_dump(self):
        """Return object legends"""
        return self.__legends

    def data_dump(self):
        """Return object data"""
        return self.__data

    def title_add(self, text):
        """Add title to object"""
        self.__desc["title"] = text
        self.__last_desc = "title"

    def title_dump(self):
        """Return object title"""
        return self.__desc["title"].strip()

    def xlab_add(self, text):
        """Add x axis label"""
        self.__desc["xlab"] = text
        self.__last_desc = "xlab"

    def xlab_dump(self):
        """Return x axis label"""
        return self.__desc["xlab"].strip()

    def ylab_add(self, text):
        """Add y axis label"""
        self.__desc["ylab"] = text
        self.__last_desc = "ylab"

    def ylab_dump(self):
        """Return y axis label"""
        return self.__desc["ylab"].strip()

    def apply_case(self, overlay):
        """Apply case pattern (sub/superscripts) to the last processed string."""
        if self.__last_desc == "else":
            strings = self.__desc[self.__last_desc]
            string = strings[len(strings) - 1]  # get the last string
        else:
            string = self.__desc[self.__last_desc]
        match = [m for m in re.finditer(self.__pattern, overlay)]
        match.reverse()  # so we would not mess up finditer indexes
        for m in match:
            if "X" in m.group(0):
                # chars are superscripted
                string = (
                    string[: m.start()]
                    + "$^{"
                    + string[m.start() : m.end()]
                    + "}$"
                    + string[m.end() :]
                )
            if "V" in m.group(0):
                # chars are subscripted
                string = (
                    string[: m.start()]
                    + "$_{"
                    + string[m.start() : m.end()]
                    + "}$"
                    + string[m.end() :]
                )
            if "F" in m.group(0):
                # chars are mapped the Greek alphabet. In our case it's omega
                if string[m.start()] == "W":
                    string = string[: m.start()] + r"$\Omega$" + string[m.end() :]
        if self.__last_desc == "else":  # push substituted string back
            self.__desc[self.__last_desc][len(strings) - 1] = string
        else:
            self.__desc[self.__last_desc] = string

    def append_last(self, text):
        """Append text to the last used self._desc"""
        if self.__last_desc == "else":
            self.__desc["else"][len(self.__desc["else"]) - 1] = (
                self.__desc["else"][len(self.__desc["else"]) - 1] + text
            )
        else:
            self.__desc[self.__last_desc] = self.__desc[self.__last_desc] + text

    def description_add(self, text):
        """Add whatever info was added to plot"""
        self.__desc["else"].append(text)
        self.__last_desc = "else"

    def description_dump(self):
        """Return whatever info was added to plot"""
        return self.__desc["else"]

    def reverse(self, val=None):
        """Set self.__reverse flag"""
        if val is not None:
            self.__reverse = val
        return self.__reverse


def top_parse(f):
    """Parse ABCI input file.
    Input file contains a number of plots, each with multiple lines.
    Every plot is stored in ABCIDATA object. List of these objects is returned"""
    objList = []  # List of objects
    currentObject = None  # Pointer to the current object
    try:
        with open(f) as text:
            newpart = True  # flag indicating that previous object ended
            for line in text:
                # parse each line of the output file and create list `objList` of
                # object of class `ABCIDATA`. Each object will contain coordinates of
                # plot points and plot style information
                # output data file cannot be parsed sequentially, so logic may be confusing
                words = line.strip().split()  # words in line
                if currentObject is not None and line[0] == " " and len(words) == 2:
                    # line with coordinates
                    # begins with space, contains two floats
                    try:
                        currentObject.insert(float(words[0]), float(words[1]))
                        continue
                    except ValueError:
                        pass  # fallthrough
                if currentObject is not None and words[0] == "SET":
                    # the only SET we are interested in is ORDER. Others just set up windows, fonts etc.
                    if len(words) > 3 and words[1] == "ORDER":
                        if words[2] == "X":
                            # order is reversed
                            currentObject.reverse(True)
                    continue
                if currentObject is not None and words[0] == "TITLE":
                    # this line is a title or label or legend or something else
                    currentObject.store_to_new(True)  # after this line begin new chunk
                    li = line.strip().split("'")
                    li = [i for i in li if len(i) > 0]
                    msg = ""
                    if len(li) > 1:
                        msg = msg.join(li[1:])
                    if len(words) > 3 and newpart:
                        # it's a title
                        currentObject.title_add(msg)
                    elif "BOTTOM" in words:
                        # it's x label
                        currentObject.xlab_add(msg)
                    elif "LEFT" in words:
                        # it's y label
                        currentObject.ylab_add(msg)
                    elif "DATA" in words and "SIZE" in words:
                        # it's a legend
                        currentObject.last_is_legend(msg)
                    else:
                        # it's something else
                        currentObject.description_add(msg)
                    newpart = False
                    continue
                if currentObject is not None and words[0] == "MORE":
                    # this line is a continuation of the previous "TITLE"
                    li = line.strip().split("'")
                    li = [i for i in li if len(i) > 0]
                    msg = ""
                    if len(li) > 1:
                        msg = msg.join(li[1:]).strip()
                    currentObject.append_last(msg)
                    continue
                if currentObject is not None and words[0] == "CASE":
                    # this line shows the positions of subscripts (V),
                    # superscripts (X) and Greek letters (F)
                    li = line.strip().split("'")
                    li = [i for i in li if len(i) > 0]
                    msg = ""
                    if len(li) > 1:
                        msg = msg.join(li[1:])
                    currentObject.apply_case(msg)
                    continue
                if currentObject is not None and words[0] == "JOIN":
                    # this line terminates previous chunk and sets the line style
                    new = True
                    if len(words) > 1 and words[1].isdigit():
                        new = True
                    if "DOTS" in words:
                        currentObject.buffer_store("dotted", new)
                    elif "DASH" in words:
                        currentObject.buffer_store("dashed", new)
                    elif "DOTDASH" in words:
                        currentObject.buffer_store("dashdot", new)
                    else:
                        currentObject.buffer_store("solid", new)
                    continue
                if words[0] == "NEW" and words[1] == "FRAME":
                    # new frame command indicates new plot
                    # therefore, adding previous object to object list and creating a new one
                    if currentObject is not None:
                        objList.append(currentObject)
                    currentObject = ABCIDATA()
                    newpart = True
                    continue
                if words[0] == "PLOT":
                    # don't really know, what this means
                    continue
            if currentObject is not None:
                objList.append(currentObject)  # if there's a new object, add it to list
    except PermissionError:
        pass  # if cannot open file, skip

    return objList
