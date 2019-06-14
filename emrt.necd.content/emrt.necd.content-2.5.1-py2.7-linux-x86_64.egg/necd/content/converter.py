from emrt.necd.content import MessageFactory as _
from z3c.form.converter import NumberDataConverter
from z3c.form.interfaces import IWidget

import zope


symbols = {
            u'decimal': u',',
            u'group': u'',
            u'list':  u';',
            u'percentSign': u'%',
            u'nativeZeroDigit': u'0',
            u'patternDigit': u'#',
            u'plusSign': u'+',
            u'minusSign': u'-',
            u'exponential': u'E',
            u'perMille': u'\xe2\x88\x9e',
            u'infinity': u'\xef\xbf\xbd',
            u'nan': ''
}


class NECDNumberDataConverter(NumberDataConverter):
    def __init__(self, field, widget):
        super(NECDNumberDataConverter, self).__init__(field, widget)
        self.formatter.symbols.update(symbols)


class NECDIntegerDataConverter(NECDNumberDataConverter):
    """A data converter for integers."""
    zope.component.adapts(
        zope.schema.interfaces.IInt, IWidget)
    type = int
    errorMessage = _('The entered value is not a valid integer literal.')
