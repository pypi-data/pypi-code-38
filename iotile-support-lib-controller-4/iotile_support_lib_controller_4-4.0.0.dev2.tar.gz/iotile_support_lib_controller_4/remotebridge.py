import time
import struct
import os
import sys
import binascii
from tempfile import NamedTemporaryFile
import subprocess
import hashlib
from iotile.core.utilities.console import ProgressBar
from iotile.core.exceptions import *
from iotile.core.hw.proxy.plugin import TileBusProxyPlugin
from iotile.core.utilities.typedargs.annotate import param, annotated, return_type, context
from iotile.core.utilities.typedargs import iprint, type_system
from iotile.core.utilities.intelhex import IntelHex

@context("RemoteBridge")
class RemoteBridgePlugin(TileBusProxyPlugin):
    """A Python interface to the untrusted remote bridge component on an IOTile Controller

    The untrusted remote bridge can be used to send scripts down to a device that are
    executed once the entire script is received, stored in flash and authenticated.
    """

    def _batch(self, iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

    def __init__(self, parent):
        super(RemoteBridgePlugin, self).__init__(parent)
        self.script = None

    def begin_script(self):
        """Indicate that we are going to start loading a script

        """

        err, = self.rpc(0x21, 0x00, result_format="L", timeout=10.0)
        return err

    def end_script(self):
        """Indicate that we are going to start loading a script

        """

        err, = self.rpc(0x21, 0x02, result_format="L")
        return err

    @return_type("integer")
    def trigger_script(self):
        """Indicate that we are going to start loading a script

        """

        err, = self.rpc(0x21, 0x03, result_format="L")
        return err

    @return_type("list(integer)")
    def query_status(self):
        """Query the status of script loading or execution

        """

        status, error = self.rpc(0x21, 0x04, result_format="LL")
        return status, error

    @param("target", "fw_tileselector", desc="Tile to reflash")
    @param("firmware", "path", "readable", desc="Firmware file to reflash with")
    def reflash_tile(self, target, firmware):
        """Synchronously reflash the tile firmware in the given slot

        """

        self.create_script()
        self.add_reflash_tile_action(target, firmware)
        self.send_script()

        self.wait_script()

    @annotated
    def wait_script(self):
        """Trigger a script and then synchronously wait for it to finish processing
        """

        self.trigger_script()
        status, error = self.query_status()
        if error != 0:
            raise HardwareError("Error executing remote script", error_code=error)

        iprint("Waiting for script to validate")
        while status == 3:
            time.sleep(0.1)
            status, error = self.query_status()
            if error != 0:
                raise HardwareError("Error executing remote script", error_code=error)


        iprint("Waiting for script to finish executing")

        while status != 0:
            if type_system.interactive:
                sys.stdout.write('.')
                sys.stdout.flush()

            time.sleep(0.1)
            status, error = self.query_status()
            if error != 0:
                raise HardwareError("Error executing remote script", error_code=error)


        if type_system.interactive:
            sys.stdout.write('\n')

    @param("firmware", "path", "readable", desc="Firmware file to reflash with")
    @param("enhanced", "bool", desc="Flag to use enhanced reflash controller record")
    def reflash_controller(self, firmware, enhanced=False):
        """Reflash the controller with new firmware

        """

        self.create_script()
        if enhanced is True:
            self.add_enhanced_reflash_controller_action(firmware)
        else:
            self.add_reflash_controller_action(firmware)
        self.send_script()

        self.trigger_script()

        iprint("Waiting 10 seconds for script to finish executing")
        time.sleep(10)
        iprint("NB, you must reconnect to the controller now until we support persistent connections across resets")

    def push_script(self, buffer, progress=None):
        """Push a byte array into the controller as a remote script

        """

        progress_bar = progress

        def update_progress(current, total):
            if progress_bar is not None:
                progress.progress(current*100/total)

        self._proxy.stream.send_highspeed(buffer, update_progress)
            
    @annotated
    def reset_script(self):
        err, = self.rpc(0x21, 0x05, result_format="L", timeout=15.0)

    @annotated
    def create_script(self):
        """Create a new empty script for downloading to a controller

        """
        self.script = bytearray()

    @param("target", "fw_tileselector", desc="Tile to reflash")
    @param("firmware", "path", "readable", desc="Firmware file to reflash with")
    def add_reflash_tile_action(self, target, firmware):
        """Add a record to our current script that reflashes a tile on the device

        """

        #FIXME: This is hardcoded data from NXP LPC824 cortex m0+ 
        offset = 6*1024
        total_size = 32*1024

        if self.script is None:
            raise ExternalError("You must create a script before adding any actions to it")

        bindata = self.load_binary_firmware(firmware, offset, total_size)

        #FIXME: Include hardware type here
        bootload_header = struct.pack("<LL8sBxxx", offset, len(bindata), target.raw_data, 0)
        self.add_record(1, bootload_header + bindata)

    def load_binary_firmware(self, firmware, offset=None, check_size=None):
        if not firmware.endswith(".elf") and not firmware.endswith(".hex"):
            raise ArgumentError("You must pass an ARM firmware image in elf/hex format", path=firmware)

        #Get a temporary file to store the binary dump
        tmpf = NamedTemporaryFile(delete=False)
        tmpf.close()

        tmp = tmpf.name

        objcopy_args = ['arm-none-eabi-objcopy', '-O', 'binary']

        try:
            if firmware.endswith(".hex"):
                objcopy_args.append('-I')
                objcopy_args.append('ihex')
            objcopy_args.append(firmware)
            objcopy_args.append(tmp)

            err = subprocess.call(objcopy_args)
            if err != 0:
                raise ExternalError("Cannot convert elf to binary file", error_code=err)
            
            with open(tmp, "rb") as f:
                bindata = f.read()

        finally:
            os.remove(tmp)

        if check_size is not None and (offset + len(bindata) != check_size):
            raise ArgumentError("Firmware image is the wrong size", actual_size=len(bindata), desired_size=(check_size - offset))

        return bindata

    def get_image_metadata(self, firmware):
        """Gets metadata of the firmware image
        """
        if not firmware.endswith(".elf") and not firmware.endswith(".hex"):
            raise ArgumentError("You must pass an ARM firmware image in elf/hex format", path=firmware)

        #Get a temporary file to store the binary dump
        tmpf = NamedTemporaryFile(delete=False)
        tmpf.close()

        tmp = tmpf.name

        try:
            if firmware.endswith(".elf"):
                err = subprocess.call(['arm-none-eabi-objcopy', '-O', 'ihex', firmware, tmp])
                if err != 0:
                    raise ExternalError("Cannot convert elf to binary file", error_code=err)
            
                hex_image = IntelHex(tmp)
            else:
                hex_image = IntelHex(firmware)

            start_address = hex_image.minaddr()

            # image_length = 0

            # image_segments = hex_image.segments()
            # for segment in image_segments:
            #     image_length += segment[1] - segment[0]

        finally:
            os.remove(tmp)

        return start_address

    @param("firmware", "path", "readable", desc="Firmware file to reflash with")
    def add_reflash_controller_action(self, firmware):
        if self.script is None:
            raise ExternalError("You must create a script before adding any actions to it")

        #This is the firmware offset specific to the con_nrf52832 with softdevice 3.0
        offset = 0x1f000

        con_image = self.load_binary_firmware(firmware)

        bootload_header = struct.pack("<LL", offset, len(con_image))
        self.add_record(2, bootload_header + con_image)

    @param("firmware", "path", "readable", desc="Firmware file to reflash with")
    def add_enhanced_reflash_controller_action(self, firmware):
        if self.script is None:
            raise ExternalError("You must create a script before adding any actions to it")

        con_image = self.load_binary_firmware(firmware)

        start_address = self.get_image_metadata(firmware)

        # TODO add compression settings and preinstall checks
        compression_settings = bytearray(16)
        preinstall_checks = bytearray(64)

        # if len(con_image) != total_length:
        #     raise ArgumentError("Firmware image length mismatch")

        bootload_header = struct.pack("<LLLBBBB16s64s", start_address, len(con_image), len(con_image),
                                         1, 0, 0, 0, compression_settings, preinstall_checks)

        self.add_record(6, bootload_header + con_image)

    def add_record(self, record_type, contents):
        """
        Add an action record to the current script with an appropriate header
        """

        record_header = record_header = struct.pack("<LBBBB", len(contents)+8, record_type, 0, 0, 0)

        self.script += record_header + contents

    def add_rpc_action(self, address, cmd, payload, resp_size=0, variable_resp=False, check_errors=False):
        """Send an RPC as part of the script

        Args:
            address (int): The addres of the tile to send the RPC to
            cmd (int): The RPC id to call
            payload (bytearray): The payload buffer for the RPC
            resp_size (int): The expected response size if the rpc gives a fixed size
            variable_resp (bool): Whether the rpc returns a variably sized object
            check_errors (bool): Whether the rpc returns a uint32_t only that is an error code 
                that we should check to ensure it's 0.

        Notes:
            Header record we are constructing is:
            typedef struct
            {
                uint16_t    command;
                uint8_t     address;
                uint8_t     variable_length_resp:1;
                uint8_t     response_length:7;
            } trub_execute_rpc_record_t;
        """

        if resp_size >= (1 << 7):
            raise ArgumentError("The expected response size is too big to fit in an RPC", resp_size=resp_size)

        if variable_resp:
            resp_length = 1
        elif check_errors:
            resp_length = (4 << 1)
        else:
            resp_length = (resp_size << 1)

        rpc_header = struct.pack("<HBB", cmd, address, resp_length)

        if check_errors:
            record_type = 4
        else:
            record_type = 3

        self.add_record(record_type, rpc_header + payload)

    @annotated
    def add_reset_action(self):
        """Reset the device
        """

        self.add_record(5, bytearray())

    @param("device_id", "integer", desc='The new UUID to set')
    def add_setuuid_action(self, device_id):
        """Set the uuid of the device to the given value
        """

        payload = struct.pack("<L", device_id)
        self.add_rpc_action(8, 0x2006, bytearray(payload), check_errors=True)

    @param("name", "string", desc="app or os")
    @param("tag", "integer", "nonnegative", desc="OS or app version to program")
    @param("version", "string", desc="X.Y version number to program.  X and Y must each be < 64")
    def add_setversion_action(self, name, tag, version="0.0"):
        """Update the controller's internal app or os tags and versions.

        The controller stores a 20 bit tag value that should uniquely identify
        the kind of OS or APP that it is running.  Each of those are asociated
        with a 6.6 bit X.Y major and minor version number.
        """

        if name not in ['app', 'os']:
            raise ArgumentError("You must specify either app or os to set_version", name=name)

        update_app = int(name == 'app')
        update_os = int(name == 'os')

        try:
            major, _, minor = version.partition('.')
            major = int(major)
            minor = int(minor)
        except ValueError:
            raise ArgumentError("Could not parse version as X.Y", version=version)

        if major < 0 or major >= 64:
            raise ArgumentError("Major version not in [0, 64)", version=version, parsed_major=major)

        if minor < 0 or minor >= 64:
            raise ArgumentError("Minor version not in [0, 64)", version=version, parsed_minor=minor)

        if tag >= (1 << 20):
            raise ArgumentError("Invalid tag that is too large, it must be < (1 << 20)", tag=tag)

        packed_version = tag | (major << 26) | (minor << 20)

        args = struct.pack("<LLBB", packed_version, packed_version, update_os, update_app)
        self.add_rpc_action(8, 0x100B, bytearray(args), check_errors=True)

    @param("user_key", "string", desc='The device key to set as 64 hex digits')
    def add_setuserkey_action(self, user_key):
        """Set the user key of a device
        """

        binkey = bytearray(binascii.unhexlify(user_key))
        if len(binkey) != 32:
            raise ArgumentError("You must pass 64 hex digits that convert into a 32 byte key", keylength=len(binkey))

        lowpayload = struct.pack("<HH16s", 0, 0, bytes(binkey[:16]))
        highpayload = struct.pack("<HH16s", 1, 0, bytes(binkey[16:]))
        self.add_rpc_action(8, 0x1007, bytearray(lowpayload), check_errors=True)
        self.add_rpc_action(8, 0x1007, bytearray(highpayload), check_errors=True)

    @param("graph_file", "path", "readable", desc="The binary sensorgraph file to load")
    def add_loadsensorgraph_action(self, graph_file):
        """Load the sensorgraph specified by the binary file graph_file

        Note that this action turns into a sequence of RPCs executed as part of the script.
        If the graph_file does not specify a reset as the first RPC, it will not erase the
        current sensor graph.  Similarly, if it does not specify persist, it will not save
        the sensor graph to flash.
        """

        with open(graph_file, "r") as f:
            lines = f.readlines()

        if len(lines) < 3:
            raise DataError("Invalid sensorgraph file that did not have a header")

        header = lines[0].rstrip()
        version = lines[1].rstrip()
        filetype = lines[2].rstrip()

        if header != "Sensor Graph":
            raise DataError("Invalid sensorgraph file that had an unknown header", expected="Sensor Graph", read=header)

        if version != "Format: 1.0":
            raise DataError("Unknown sensorgraph file version", expected="Format: 1.0", read=version)

        if filetype != "Type: BINARY":
            raise DataError("Sensorgraph file is not in ascii format", excepted="Type: BINARY", read=filetype)

        cmds = [x.strip() for x in lines[3:] if not x.startswith('#') and not x.strip() == ""]

        for cmd in cmds:
            rpc_id, _, arg = cmd.partition(":")

            arg = arg.strip()
            rpc_id = rpc_id.strip()

            if arg == "":
                arg = bytearray()
            else:
                arg = bytearray(binascii.unhexlify(arg))

            rpc_id = int(rpc_id, 16)
            self.add_rpc_action(8, rpc_id, arg, check_errors=True)

    def add_header(self, script):
        """Add a hashed header to the script for verification

        """

        #Script header is 2 uint32_t variables and a 16 byte hash code
        length = len(script) + 4 + 4 + 16
        header = struct.pack("<LL", 0x1F2E3D4C, length)

        script = bytearray(header) + script

        sha = hashlib.sha256()
        sha.update(script)

        hashval = bytearray(sha.digest())[:16]
        return hashval + script

    @param("outfile", "path", "writeable", desc="Path of output file")
    def dump_script(self, outfile):
        """Dump the current script to a file
        """

        if self.script is None:
            raise HardwareError("You must first load a script before you can dump it")

        #Add a header to our script
        script = self.add_header(self.script)

        with open(outfile, "wb") as file:
            file.write(script)

    @param("script", "path", desc="Optional file to load script from")
    def send_script(self, script=None):
        """Send the currently loaded script to the attached controller

        If a script file is instead supplied as an argument, use that instead
        of the currently loaded one.

        """

        if script is not None:
            with open(script, "rb") as sfile:
                script = sfile.read()
        else:
            if self.script is None:
                raise HardwareError("You must first load a script before you can send it to a device")

            #Add a header to our script
            script = self.add_header(self.script)

        err = self.begin_script()
        if err:
            raise HardwareError("Error beginning script", error_code=err)

        progress = ProgressBar("Downloading script", 100)

        progress.start()
        err = self.push_script(script, progress)
        progress.end()
        if err:
            raise HardwareError("Error beginning script", error_code=err)

        err = self.end_script()
        
        if err:
            raise HardwareError("Error beginning script", error_code=err)
