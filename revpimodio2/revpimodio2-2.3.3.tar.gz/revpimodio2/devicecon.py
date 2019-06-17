# -*- coding: utf-8 -*-
"""Modul fuer die Verwaltung der Connectdevices."""
__author__ = "Sven Sager"
__copyright__ = "Copyright (C) 2018 Sven Sager"
__license__ = "LGPLv3"
from serial import Serial
from queue import Queue
from threading import Thread


class BndEntry():

    def __init__(self, mac, link_type, name):
        self.mac = mac
        self.link_type = link_type
        self.name = name


class SerialReader(Thread):

    def __init__(self, connection, echo=False):
        super().__init__()
        self.daemon = True
        self._con = connection
        self._echo = echo
        self._run = True

        self.q_at = Queue()

    def run(self):
        while self._run:
            if self._con.read(1) != b'\xcc':
                # TODO: Falscher Framestart. Was soll hier passieren?
                #raise RuntimeError("wrong mux frame start")
                continue

            mux_channel = int.from_bytes(self._con.read(1), "little")
            rsp_length = int.from_bytes(self._con.read(1), "little")
            rsp_data = self._con.read(rsp_length)

            # Ausgabe auf Console spiegeln
            if self._echo:
                print(mux_channel, rsp_length, rsp_data)

            # Daten zuordnen
            if mux_channel == 255:
                # AT Ausgaben
                for line in rsp_data.split(b'\r\n'):
                    if line:
                        self.q_at.put_nowait(line)

        print("reader end")

    def stop(self):
        """Beendet den SerialReader."""
        self._run = False
        self._con.cancel_read()


class ConBluetooth():

    def __init__(self, devpath="/dev/ttyConBridge", baud=115200, echo=False):
        """Init ConBluetooth class."""
        if not isinstance(devpath, str):
            raise TypeError("devpath must be <class 'str'>")
        if not isinstance(baud, int):
            raise TypeError("baud must be <class 'int'>")
        if not isinstance(echo, bool):
            raise TypeError("echo must be <class 'bool'>")

        self._baud = baud
        self._con = Serial()
        self._devpath = devpath
        self._echo = echo
        self._terminator = b'\r'

    def __del__(self):
        """Delete class."""
        if self._con.is_open:
            self.hangup()

    def _cmd_bool(self, cmd):
        """Sendet UART Kommando und wertet Status aus.
        @param cmd AT-Befehl ohne Steuerzeichen
        @return True, wenn erfolgreich, sonst False"""
        if not self._con.is_open:
            raise RuntimeError("connection is closed")

        if not isinstance(cmd, bytes):
            raise TypeError("cmd must be <class 'bytes'>")
        if len(cmd) > 255:
            raise ValueError("cmd is too long max 255 bytes")

        # Befehl erzeugen und senden
        cmd += self._terminator
        cmd = b'\xcc\xff' + len(cmd).to_bytes(1, "little") + cmd
        self._con.write(cmd)

        # FIXME: Blockiert
        response = self.sr.q_at.get()

        # Rückgabe prüfen und auswerten
        if response == b'OK':
            return True
        return False

    def _cmd_list(self, cmd):
        """Sendet UART Kommando und wertet Ergebnis aus.
        @param cmd AT-Befehl ohne Steuerzeichen
        @return Liste mit Ergebnissen"""
        if not self._con.is_open:
            raise RuntimeError("connection is closed")

        if not isinstance(cmd, bytes):
            raise TypeError("cmd must be <class 'bytes'>")

        # Befehl erzeugen und senden
        cmd += self._terminator
        cmd = b'\xcc\xff' + len(cmd).to_bytes(1, "little") + cmd
        self._con.write(cmd)

        # Liste erstellen
        lst_response = []
        while True:
            # FIXME: Blockiert
            buff = self.sr.q_at.get()

            # Fertigstellung auswerten
            if buff == b'OK' or buff == b'ERROR':
                return lst_response

            lst_response.append(buff.decode())

    def _get_terminator(self):
        """Getter fuer Terminator."""
        return self._terminator.decode()

    def _set_terminator(self, value):
        """Getter fuer Terminator."""
        if not isinstance(value, str):
            raise TypeError("value must be <class 'str'>")
        self._terminator = value.encode()

    def accept_incomming_call(self):
        """This command accepts an incomming call."""
        if not self._cmd_bool(b'ATA'):
            raise RuntimeError("could not accept incomming call")

    def bonded_device_list_size(self, size):
        """This command reduces the number of decies 1 - 8.
        @param size Max bonded devices"""
        if not isinstance(size, int):
            raise TypeError("size must be <class 'int'>")
        if 0 <= size <= 8:
            raise ValueError("size must be 0 - 8")

        if not self._cmd_bool(b'AT+BNDSIZE=' + str(size).encode()):
            raise RuntimeError("could not accept incomming call")

    def configure_pairable_mode(self, mode):
        """Controls the pairable mode.
        @param mode 0=Only bonded / 1=bonded and new devices"""
        if not isinstance(mode, int):
            raise TypeError("mode must be <class 'int'>")
        if 0 <= mode <= 1:
            raise ValueError("mode must be 0 - 1")

        if not self._cmd_bool(b'AT+BPAIRMODE=' + str(mode).decode()):
            raise RuntimeError("could not set pairable mode")

    def disconnect(self):
        """Dissconnects the existing Bluetooth connection."""
        if not self._cmd_bool(b'ATH'):
            raise RuntimeError("could not disconnect bluetooth connection")

    def hangup(self):
        """Beendet die serielle Kommunikation."""
        if not self._con.is_open:
            raise RuntimeError("connection is closed")

        # SerialReader herunterfahren
        self.sr.stop()
        self.sr.join()

        # Verbindung schließen
        self._con.close()

    def load_factory_defaults(self):
        """The factory-default values will be loaded."""
        if not self._cmd_bool(b'AT&F'):
            raise RuntimeError("could not load factory defaults")

    def load_stored_parameters(self):
        """Load all parameters from non-volatile RAM."""
        if not self._cmd_bool(b'AT+LOAD'):
            raise RuntimeError("could not load stored parameters")

    def local_device_name(self, name, mac_signs=0):
        """Set local device name."""
        if not isinstance(name, str):
            raise TypeError("name must be <class 'str'>")
        if not (isinstance(mac_signs, int) and 0 <= mac_signs <= 12):
            raise TypeError("mac_signs must be <class 'str'>")

        # Name in Bytes umwandeln
        name = name.encode()
        if len(name) > 25 - mac_signs:
            raise ValueError("max length of name is 25 signs incl. mac_signs")

        cmd = b'AT+BNAME' + name
        if mac_signs > 0:
            cmd += b'%' + str(mac_signs).encode() + b'a'

        if not self._cmd_bool(cmd):
            raise RuntimeError("could not load factory defaults")

    def open(self):
        # Serielle Schnittstelle konfigurieren
        self._con.baudrate = self._baud
        self._con.port = self._devpath
        self._con.timeout = 1
        self._con.open()

        # Start MUX Mode
        self._con.write(b'\xcc\xff\x0aAT+BMUX=1\r')
        # Send long result messages
        self._con.write(b'\xcc\xff\x05ATV1\r')
        # Do not supress results
        self._con.write(b'\xcc\xff\x04ATQ\r')
        
        #self._con.reset_input_buffer()
        print(self._con.read(100))

        # SerialReader vorbereiten
        self.sr = SerialReader(self._con, self._echo)
        self.sr.start()

        if not self._cmd_bool(b'AT'):
            raise RuntimeError("could not get AT ping")

    def own_device_address(self):
        """Get own Bluetooth device address.
        @return Device address as <class 'str'>"""
        lst = self._cmd_list(b'AT+BOAD')
        return lst[0]

    def reset_device(self):
        """Reset the bluetooth device with hardware reset."""
        # FIXME: Blockiert, da keine Rückmeldung
        self._cmd_bool(b'AT+RESET')

#    def send_raw(self, payload):
#        """Sendet Bytes an die Schnittstelle.
#        @param payload Bytes zum senden."""
#        if not isinstance(payload, bytes):
#            raise TypeError("payload must be <class 'bytes'>")
#
#        self._con.write(payload)

    def bonded_device_list(self):
        """Shows information about bonded devices."""
        # TODO: Bonded Device List verarbeiten
        return self._cmd_list(b'AT+BNDLIST')

    def store_active_configuration(self):
        """The active configuration is stored in non-volatile memory."""
        if not self._cmd_bool(b'AT&W'):
            raise RuntimeError("could not store active configuration")

    terminator = property(_get_terminator, _set_terminator)


""" Missing:
Return to Online State (S. 27) !!!!!!!!

Read Absolute RSSI Value (S. 13)
SSP I/O Capabilities (S. 13)
SSP Man in the middle protection (S. 14)
Activate Multiplexing Mode (S. 14)
Delete Bonding Information (S. 16)
Storage Mode for Bonds (S. 16)
RSSI Output at I2C Interface (S. 18)
Secure Simple Pairing Configuraiton (S. 19)
SSP Passkey Response (S. 19)
SSP Debug Mode (S. 20)
Update Interval for Radio Statistics (S. 20)
Initiate Bluetooth Link (S. 21)
Autodial Mode (S. 23)
Autodial Parameters (S. 23)
Set an Autodial String(S. 24)
Display Version Informatio (S. 25)
Config of Pin IOA (S. 25)
Config of Pin IOB (S. 26)
Config of Pin IOC (S. 26)
Set NFC Mode (S. 27)
Maximum Output Power (S. 28)
AT S Register (S. 28)
Set UART Interface Control (S. 29)
"""


class ConBluetoothClassic(ConBluetooth):

    def encryption(self, active):
        """Enable or disable encryption.
        @param active Set True=on, False=off"""
        if not isinstance(active, bool):
            raise TypeError("active must be <class 'bool'>")

        if not self._cmd_bool(b'AT+BCRYPT=' + str(int(active)).encode()):
            raise RuntimeError("could not set encryption")

    def device_pin(self, pin):
        """Set the device pin for BT 2.0 devices.
        @param pin PIN with up to 16 digits"""
        if not isinstance(pin, int):
            raise TypeError("pin must be <class 'int'>")

        pin = str(pin)
        if len(pin) > 16:
            raise ValueError("pin is too long max 16 digits")

        if not self._cmd_bool(b'AT+BPIN=' + pin.encode()):
            raise RuntimeError("could not set device pin")

    def fast_connection_mode(self, active):
        """Enable or disable fast conneciton mode.
        @param active Set True=on, False=off"""
        if not isinstance(active, bool):
            raise TypeError("active must be <class 'bool'>")

        if not self._cmd_bool(b'AT+BFCON=' + str(int(active)).encode()):
            raise RuntimeError("could not set fast connection mode")

    def legacy_pairing_requirement(self, active):
        """Enable or disable legacy pairing requirement for BT 2.0.
        @param active Set True=on, False=off"""
        if not isinstance(active, bool):
            raise TypeError("active must be <class 'bool'>")

        if not self._cmd_bool(b'AT+BLPREN=' + str(int(active)).encode()):
            raise RuntimeError("could not set legacy pairing requirement")

    def search_devices(self):
        """Discover bluetooth devices (takes 10 seconds)."""
        # TODO: Kann das auch nicht blockend gemacht werden?
        return self._cmd_list(b'AT+BINQ')


""" Missing Classic:
Bluetooth Class of Device (S. 31)
Discover services of device (S. 35)
Bond with a bluetooth device (S. 36)
Own service profile (S. 36)
Scanning capability (S. 37)
Block Size (S. 38)
Sniff Mode (S. 38)
Local Service Name (S. 39)
"""
