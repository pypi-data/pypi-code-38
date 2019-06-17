from ivi.agilent import agilentU2001A
from ivi import decode_ieee_block
from array import array


class GOU2001A(agilentU2001A):
    """
    Gradient One's customized agilent U2001A object
    """
    def __init__(self, visa_address="USB::0x2a8d::0x2b18::INSTR"):
        super(agilentU2001A, self).__init__(visa_address)
        self._write("sense:detector:function normal")
        self.trace = self.TraceCommands(self)
        self.trigger = self.TriggerCommands(self)

    class TraceCommands:
        def __init__(self, dev_reference):
            self.dev = dev_reference

        @property
        def state(self):
            return int(self.dev._ask("trace:state?"))

        @state.setter
        def state(self, new_val):
            self.dev._write("trace:state "+str(new_val))

        @property
        def offset_time(self):
            return float(self.dev._ask("trace:offset:time?"))

        @offset_time.setter
        def offset_time(self, new_val):
            self.dev._write("trace:offset:time "+str(new_val))

        @property
        def time(self):
            return float(self.dev._ask("trace:time?"))

        @time.setter
        def time(self, new_val):
            self.dev._write("trace:time "+str(new_val))

        def get_data(self):
            self.dev._write("trace:data? hres")
            return array('f', decode_ieee_block(self.dev._read_raw()))

    class TriggerCommands:
        def __init__(self, dev_reference):
            self.dev = dev_reference

        @property
        def source(self):
            return self.dev._ask("trigger:source?")

        @source.setter
        def source(self, new_val):
            self.dev._write("trigger:source "+new_val)

        @property
        def level(self):
            return float(self.dev._ask("trigger:level?"))

        @level.setter
        def level(self, new_val):
             self.dev._write("trigger:level "+str(new_val))

        @property
        def slope(self):
            return self.dev._ask("trigger:slope?")

        @slope.setter
        def slope(self, new_val):
            self.dev._write("trigger:slope "+new_val)