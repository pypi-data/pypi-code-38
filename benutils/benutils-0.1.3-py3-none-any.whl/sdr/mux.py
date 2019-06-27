# -*- coding: utf-8 -*-

"""package benutils
author    Benoit Dubois
copyright Femto Engineering, 2019
brief     Signal(De)Mux classes.
details   Implement (de)multiplexing for pyQt signal.
"""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, SIGNAL, SLOT


#==============================================================================
class Demux2(QObject):
    """Class Demux2.
    """

    outUpdated = pyqtSignal('PyQt_PyObject')
    in0Updated = pyqtSignal('PyQt_PyObject')
    in1Updated = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent=None):
        """The constructor.
        :returns: None
        """
        super().__init__(parent)
        self._out = 0
        self.in0Updated.connect(self.outUpdated)

    def in0(self, arg):
        self.in0Updated.emit(arg)

    def in1(self, arg):
        self.in1Updated.emit(arg)

    def select_out(self, out_idx):
        """Select output.
        :param d_factor: decimation factor (int)
        :returns: None
        """
        if not (0 < out_idx < 1):
            raise AttributeError("output index must be 0 or 1")
        if out_idx == self._out:
            return
        self._out = out_idx
        if out_idx == 0:
            self.in1Updated.disconnect(self.outUpdated)
            self.in0Updated.connect(self.outUpdated)
        else:
            self.in0Updated.disconnect(self.outUpdated)
            self.in1Updated.connect(self.outUpdated)
        

#==============================================================================
class SignalMux(QObject):
    """Class SignalMux.
    from: https://doc.qt.io/archives/qq/qq08-action-multiplexer.html#signalmultiplexinginpractice
    """

    current_object_changed = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent=None):
        """The constructor.
        :returns: None
        """
        super().__init__(parent=parent)
        self._object = None
        self._connections = list()
        
    def connect(self, sender=None, signal=None, receiver=None, slot=None):
        conn = {'sender':sender, 'receiver':receiver, \
                'signal':signal, 'slot':slot}
        self._connections.append(conn)
        self._connect(conn)

    def disconnect(self, sender=None, signal=None, receiver=None, slot=None):
        for conn in self._connections:
            if conn['sender'] == sender and \
               conn['signal'] == signal and \
               conn['slot'] == slot:
                self._disconnect(conn)
                self._connections.remove(conn)
                return True
            elif conn['signal'] == signal and \
                 conn['receiver'] == receiver and \
                 conn['slot'] == slot:
                self._disconnect(conn)
                self._connections.remove(conn)
                return True
        return False

    def current_object(self):
        return self._object

    @pyqtSlot(object)
    def set_current_object(self, new_object):
        if new_object == self._object:
            return

        for conn in self._connections:
            self._disconnect(conn)
        self._object = new_object
        for conn in self._connections:
            self._connect(conn)

        self.current_object_changed.emit(self._object)

    def _connect(self, conn):
        if self._object is None:
            return
        if conn['sender'] is None and conn['receiver'] is None:
            return
    
        if conn['sender'] is not None:
            super().connect(conn['sender'], SIGNAL(conn['signal']), self._object, SLOT(conn['slot']))
        else:
            super().connect(self._object, SIGNAL(conn['signal']), conn['receiver'], SLOT(conn['slot']))
    
    def _disconnect(self, conn):
        if self._object is None:
            return
        if conn['sender'] is None and conn['receiver'] is None:
            return
    
        if conn['sender'] is not None:
            super().disconnect(conn['sender'], conn['signal'], self._object, conn['slot'])
        else:
            super().disconnect(self._object, conn['signal'], conn['receiver'], conn['slot'])



#==============================================================================
if __name__ == '__main__':

    class Sender(QObject):

        ssignal = pyqtSignal(str)

        def __init__(self, parent=None):
            super().__init__(parent=parent)

        def send(self, msg):
            self.ssignal.emit("message " + str(msg) + " send from " + str(self))


    class Receiver(QObject):

        def __init__(self, parent=None):
            super().__init__(parent=parent)
        
        @pyqtSlot(str)
        def rslot(self, msg):
            print("slot() received:", msg)


    MUX = SignalMux()
    S1 = Sender()
    S2 = Sender()
    R1 = Receiver()
    #R2 = Receiver()

    """print(type(R1.rslot))
    print(type(SLOT("rslot(str)")), SLOT("rslot(str)"))
    print(type(SIGNAL("ssignal(str)")), SIGNAL("ssignal(str)"))
    """
    #S1.ssignal.connect(R1.rslot)
    #QObject().connect(S1, SIGNAL("ssignal(str)"), R1, SLOT("rslot(str)"))
    #S1.send("Basic Coucou1")
    #S1.ssignal.disconnect(R1.rslot)
    #QObject.disconnect(S1, SIGNAL("ssignal(str)"), R1, SLOT("rslot(str)"))

    #print("AAAAAAAAA")
    
    MUX.connect(sender=S1, signal=SIGNAL("ssignal(str)"), slot=SLOT("rslot(str)"))
    #MUX.connect(sender=S1, signal=S1.ssignal, slot=SLOT("rslot(str)"))
    
    MUX.connect(sender=S2, signal=SIGNAL("ssignal(str)"), slot=SLOT("rslot(str)"))    
    MUX.connect(signal=SIGNAL("ssignal(str)"), receiver=R1, slot=SLOT("rslot(str)"))
    #MUX.connect(signal=SIGNAL("ssignal(str)"), receiver=R2, slot=SLOT("rslot(str)"))
    print("Connected")

    MUX.set_current_object(S1)
    
    print("Mux from S1:", S1)
    S1.send("Coucou1")

    """
    MUX.set_current_object(S2)
    print("Mux from S2:", S2)
    S1.send("ReCoucou1")
    S2.send("ReCoucou2")

    MUX.disconnect(signal=Sender.signal, receiver=R1, slot=Receiver.slot)
    MUX.disconnect(sender=S1, signal=Sender.signal, slot=Receiver.slot)    
    MUX.disconnect(sender=S2, signal=Sender.signal, slot=Receiver.slot)
    print("Disconnected")"""
