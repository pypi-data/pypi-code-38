from enum import Enum
from typing import TypeVar


class GRPCConfig:
    ip = "34.223.5.196:3001"
    # ip = "127.0.0.1:3001"

    TOKEN = "budTest"


class GenericType:
    T = TypeVar('T')
    PT = TypeVar('PT')
    O = TypeVar('O')


class FieldType(Enum):
    TEXT = 'TEXT'
    DATETIME = 'DATETIME'
    RECORD_REFERENCE = 'RECORD_REFERENCE'
    NUMBER = 'NUMBER'
    MULTI_SELECT = 'MULTI_SELECT'
    SELECT = 'SELECT'
    # FORMULA = 'FORMULA'
    MULTI_ATTACHMENT = 'MULTI_ATTACHMENT'
    # LOOKUP = 'LOOKUP'


class DateFormat(Enum):
    LOCAL = 'LOCAL'  # 2019-05-23
    FRIENDLY = 'FRIENDLY'  # MMM Do, YYYY 2019年5月23日
    EURO = 'EURO'  # D/M/YYYY 23/5/2019
    ISO = 'ISO'  # YYYY-MM-DD  2019-05-23


class TimeFormat(Enum):
    TWELVE_HOUR = 'TWELVE_HOUR'
    TWOFOUR_HOUR = 'TWOFOUR_HOUR'


class ViewType(Enum):
    GRID = 'GRID'
    TIMELINE = 'TIMELINE'


class TableField(Enum):
    tableData = 'tableData'
    viewDatas = 'viewDatas'
    rows = 'rows'
    id = 'id'
    cells = 'cells'
    columnId = 'columnId'
    value = 'value'
    cell_type = 'type'
    text = 'text'


class Source(Enum):
    EXTERNAL_API = 'EXTERNAL_API'
    USER = 'USER'
    SAGA = 'SAGA'


class CoreColor(Enum):
    lightRed = 'lightRed'
    blue = 'blue'
    red = 'red'
    gray = 'gray'
    magenta = 'magenta'
    yellow = 'yellow'
    orange = 'orange'
    green = 'green'
    black = 'black'
    pink = 'pink'
    purple = 'purple'
    lightBlue = 'lightBlue'
    lightGray = 'lightGray'
    lightMagenta = 'lightMagenta'
    lightYellow = 'lightYellow'
    lightOrange = 'lightOrange'
    lightGreen = 'lightGreen'
    lightBlack = 'lightBlack'
    lightPink = 'lightPink'
    lightPurple = 'lightPurple'


class SelectColor(Enum):
    blue = 'blue'
    cyan = 'cyan'
    teal = 'teal'
    green = 'green'
    yellow = 'yellow'
    orange = 'orange'
    red = 'red'
    pink = 'pink'
    purple = 'purple'
    gray = 'gray'


class Icon(Enum):
    briefcase = 'briefcase'
    untitle = 'untitle'
    asterisk = 'asterisk'
    barChart = 'barChart'
    check = 'check'
    circleBlank = 'circleBlank'
    cloud = 'cloud'
    barcode = 'barcode'
    beaker = 'beaker'
    bell = 'bell'
    bolt = 'bolt'
    book = 'book'
    bug = 'bug'
    building = 'building'
    bullhorn = 'bullhorn'
    calculator = 'calculator'
    calendar = 'calendar'
    camera = 'camera'
    sun = 'sun'
    flow = 'flow'
    coffee = 'coffee'
    handUp = 'handUp'
    anchor = 'anchor'
    cogs = 'cogs'
    comment = 'comment'
    compass = 'compass'
    creditCard = 'creditCard'
    dashboard = 'dashboard'
    edit = 'edit'
    food = 'food'


class UpdateAction(Enum):
    SET_VALUE = 'SET_VALUE'
    ADD_VALUE = 'ADD_VALUE'
    REMOVE_VALUE = 'REMOVE_VALUE'
