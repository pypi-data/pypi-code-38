"""This module sets the connection to the BK scanner"""

import socket
import logging
import sys
import cv2
import numpy as np
from sksurgerybk.pyigtlink.pyIGTLink import PyIGTLink, ImageMessage


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class BK5000():
#pylint:disable=too-many-instance-attributes

    """This class sets the TCP connection with the BK scanner"""

    def __init__(self, timeout, frames_per_second):
        """ The DataSourceWorker constructor.

        Sets a number of class members.

        Parameters:
        timeout(positive float): the connection timeout in seconds.
        frames_per_second(positive integer): the expected fps from the \
                                             BK scanner
        """
        self.data = None
        self.timeout = timeout
        self.frames_per_second = frames_per_second
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.minimum_size = None
        self.packet_size = 1024
        self.request_stop_streaming = False
        self.is_streaming = False
        self.image_size = [0, 0]
        self.pixels_in_image = 0
        self.buffer = bytearray()
        self.np_buffer = None
        self.img = None
        self.rgb_img = None
        self.convert_to_rgb = False
        self.scan_geometry = {}
        self.valid_frame = False

        self.control_bits = [1, 4, 27]
        self.flipped_control_bits = [bit ^ 0xFF for bit in self.control_bits]

    def __del__(self):
        """ Close the socket on object deletion/app exit. """
        logging.debug("Deleting object, closing socket")
        self.socket.close()

    def enable_rgb_output(self):
        """
        The 'QUERY:GRAB_FRAME "ON"` gets the BK to stream
        greyscale data (e.g. 640 x 480 x 1),
         some applications might want this in RGB format (640 x 480 x 3)
        """
        self.convert_to_rgb = True

    def generate_command_message(self, message):
        #pylint:disable=no-self-use
        """ Append 0x01 and 0x04 to start/end of message before sending

        Parameters:
        message(string): the message to be sent"""
        char_start = bytearray.fromhex("01").decode()
        char_end = bytearray.fromhex("04").decode()

        message_to_send = char_start + message + char_end

        message_length = len(message_to_send)
        logging.debug("Message to send: %s Size: %s", \
             message_to_send, message_length)

        return message_to_send

    def send_command_message(self, message):
        """Send a message through the socket.

        Implements a couple of checks to verify the
        message has been sent correctly.

        Parameters:
        message(string): the message to be sent
        """

        message_to_send = self.generate_command_message(message)
        try:
            bytes_sent = self.socket.send(message_to_send.encode())
            is_ok = True
            # Check the sent went OK.
            if bytes_sent != len(message_to_send):
                is_ok = False
                raise IOError(
                    "Failed to send message: {:} due to size mismatch: {:} \
                different from {:} bytes sent.".format(message_to_send,
                                                       len(message_to_send),
                                                       bytes_sent))
            return is_ok
        except socket.error as error_msg:
            raise IOError("An error: {:} has occured while trying to send \
            the message: {:}.".format(error_msg, message_to_send))

    def receive_response_message(self, expected_size=1024):
        """Receive a message

        Stores it under the data class member

        Parameters:
        expected_size(int): the receive message size in bytes
        """
        actual_size = expected_size + 2 # Due to start/end terminator
        data_with_terminators = self.socket.recv(actual_size)
        self.data = data_with_terminators[1:-1]
        is_ok = True
        if len(self.data) > expected_size:
            is_ok = False
            raise IOError(
                "Failed to receive message: {:} due to size mismatch: {:} \
            different from {:} bytes received.".format(self.data,
                                                       len(self.data),
                                                       expected_size))
        return is_ok
    def request_stop(self):
        """Set the appropriate class member"""
        self.request_stop_streaming = True

    def disconnect_from_host(self):
        """ Disconnects the client from the host.

        If the socket is already closed, a recv() call
        will throw an error. If it doesn't, we can close the socket.
        """
        #pylint:disable=bare-except
        logging.info("Attempting to close socket.")
        try:
            self.socket.recv(self.packet_size)
            self.socket.close()

        except:
            logging.info("Socket already closed.")

    def stop_streaming(self):
        """
        Send a message to stop the streaming.
        send_command_message and receive_response_message
        will throw errors if there is a problem with the socket connection.
         """
        stop_message = 'QUERY:GRAB_FRAME \"OFF\",{:};'.\
        format(self.frames_per_second)
        self.send_command_message(stop_message)
        self.receive_response_message()
        self.is_streaming = False
        self.request_stop_streaming = False

    def start_streaming(self):
        """ Send a message to start the streaming """
        start_message = 'QUERY:GRAB_FRAME \"ON\",{:};'.\
        format(self.frames_per_second)
        self.send_command_message(start_message)
        self.receive_response_message()
        self.is_streaming = True

    def connect_to_host(self, address, port):
        """ Connects the client to the host/serverself.

        Implements a try/except block to catch potential errors.

        Parameters:
        address(string): the IP address
        port(integer): the port
        """
        try:
            self.socket.connect((address, port))
        except socket.error as error_msg:
            self.socket.close()
            raise IOError(
                "An error: {:} has occured while trying to connect to: {:} \
            with port: {:}".format(error_msg, address, port))

    def query_win_size(self):
        """ Query the BK5000 for the window/image size """
        query_win_size_message = "QUERY:US_WIN_SIZE;"
        self.send_command_message(query_win_size_message)
        self.receive_response_message(expected_size=25)
        self.parse_win_size_message(self.data.decode())

    def parse_win_size_message(self, message):
        """Extrack the size of the US window from the response message

        Message has format "DATA:US_WIN_SIZE 640,480;"

        Parameters:
        message(string): the received message """

        # Split on spaces, get the final token, strip the ; and split into
        # the two integers.
        logging.info("Parsing window size message %s", message)
        dim_part_of_message = message.split()[-1].strip(';').split(',')
        self.image_size = [int(s) for s in dim_part_of_message]
        self.pixels_in_image = self.image_size[0] * self.image_size[1]

        logging.info("Window size: %s", self.image_size)

    def query_scanarea(self):
        """ Query the BK5000 for the scan area.
        (width/height/scanning depth etc.) """
        query_scanarea_message = "QUERY:B_GEOMETRY_SCANAREA:A;"
        self.send_command_message(query_scanarea_message)
        self.receive_response_message()
        self.parse_scanarea_message()

    def parse_scanarea_message(self):
        #pylint:disable = bad-whitespace
        """ Separate the scanarea response msssage into the separate
        components.

        Message has format:
        <StartLineX>,<StartLineY>,<StartLineAngle>,<StartDepth>,
        <StopLineX>,<StopLineY>,<StopLineAngle>,<StopDepth>

        Example message:
        DATA:B_GEOMETRY_SCANAREA:A 0.0017218,-0.000171398,
        1.37236,0,-0.00174855,-0.000176821,1.77236,0.0203479; """

        # Strip out the text part of the message, and the trailing ;
        # Then split into the separate values and convert to float.
        msg = self.data.decode('utf-8').strip("DATA:B_GEOMETRY_SCANAREA:A ") \
                                       .strip(";")
        values = [float(value) for value in msg.split(',')]

        self.scan_geometry['StartLineX']        =  values[0]
        self.scan_geometry['StartLineY']        =  values[1]
        self.scan_geometry['StartLineAngle']    =  values[2]
        self.scan_geometry['StartDepth']        =  values[3]
        self.scan_geometry['StopLineX']         =  values[4]
        self.scan_geometry['StopLineY']         =  values[5]
        self.scan_geometry['StopDepthAngle']    =  values[6]
        self.scan_geometry['StopDepth']         =  values[7]


    def find_first_a_not_preceded_by_b(self, start_pos, a, b):
        #pylint:disable=invalid-name
        """
        Find the first instance of 'a' in an array that isn't preceded by 'b'

        :param start_pos: Index in array to begin search at
        :type start_pos: integer
        :param a: Value to find
        :type a: integer
        :param b: Value not to precede a
        :type b: integer
        :return: Index of first a not preceded by b, -1 if none found
        :rtype: integer
        """

        found = -1

        trimmed_buffer = self.np_buffer[start_pos:]
        if trimmed_buffer[0] == a: # First item can't be preceded by anything
            found = 0

        else:

            # Find all instances of a, then search within these values
            # for one which isn't preceded by b
            a_idx = np.where(trimmed_buffer == a)[0]
            not_b_idx = np.where(trimmed_buffer[a_idx - 1] != b)[0]

            if not_b_idx.size > 0:
                first_a_not_preceded_by_b_idx = a_idx[not_b_idx]
                found = start_pos + first_a_not_preceded_by_b_idx[0]

        return found

    def clear_bytes_in_buffer(self, start, end):
        """
        Clear a set of bytes in bytearray buffer

        :param start: Start index
        :type start: integer
        :param end: End integer
        :type end: integer
        """

        logging.debug("Start: %i End: %i", start, end)

        # Can't delete past the end of the buffer
        if end >= len(self.buffer):
            end = len(self.buffer)

        del self.buffer[start:end]

    def decode_image(self):
        """
        Process the stream of data received from the BK5000 and convert
        it into a numpy array which represents the ultrasound image.

        Control bytes are 1, 4 and 27. Flipped control bytes (1s complement
        of control bytes) are 254, 251, 228.
        Any time a flipped control bytes occurs after a 27,
        the value should be flipped and the preceding 27 deleted.
        See page 9 of 142 in BK doc PS12640-44 for further details.
        """

        # Find all locations of '27'
        uc27_idx = np.where(self.np_buffer == self.control_bits[2])[0]

        idx_to_del = np.array([], dtype=np.uint8)

        # Find each time a flipped_control_bit comes after a '27'
        for bit in self.flipped_control_bits:
            idx = np.where(self.np_buffer[uc27_idx + 1] == bit)[0]
            idx_to_del = np.append(idx_to_del, uc27_idx[idx])

        # Flip the bits that follow
        self.np_buffer[idx_to_del + 1] ^= 0xFF

        result = np.delete(self.np_buffer, idx_to_del)

        return result

    def receive_image(self):
        """
        Scan the incoming data stream to find the start and end
        of the image data.

        See BK doc PS12640-44 for further details.
        """

        # self.buffer contains the received TCP data
        # We also want a numpy representation of this.
        # Some operations are simpler to do on a bytearray than np array
        self.np_buffer = np.frombuffer(self.buffer, dtype=np.uint8)

        valid_frame = False
        msg_start_idx = self.find_first_a_not_preceded_by_b(0, 0x01, 0x27)

        if msg_start_idx < 0:
            logging.warning("Failed to find start of message character. \
                This suggets there is junk in the buffer")
            self.buffer.clear()
            return valid_frame

        msg_end_idx = self.find_first_a_not_preceded_by_b(
            msg_start_idx, 0x04, 0x27)

        if msg_end_idx <= msg_start_idx:
            logging.debug("Failed to find end of message character. \
                This is OK if message is still incoming.")
            return valid_frame

        # There isn't a standard way to do the buffer.find operation on a
        # numpy array e.g. find a sequence of values,
        # so we use the bytearray function instead.

        # utf-8 to be compatible with buffer
        img_msg = "DATA:GRAB_FRAME".encode('utf-8')
        img_msg_index = self.buffer.find(img_msg, msg_start_idx)

        if not (img_msg_index != -1 and # i.e. it was found
                msg_start_idx < img_msg_index < msg_end_idx):

            logging.warning("Received a non-image message, \
                    which I wasn't expecting.")

            self.clear_bytes_in_buffer(0, msg_end_idx + 1)
            return valid_frame

        logging.debug("Starting decode step.")
        hash_char = self.buffer.find('#'.encode('utf-8'), msg_start_idx)
        size_of_data_char = hash_char + 1

        start_image_char = size_of_data_char + \
                           1 + 4 + \
                           self.buffer[size_of_data_char] - ord('0') # ASCII

        end_image_char = msg_end_idx - 2

        self.np_buffer = self.np_buffer[start_image_char:end_image_char + 1]

        result = self.decode_image()

        self.img = result[:self.pixels_in_image] \
                  .reshape(self.image_size[1], self.image_size[0])

        # np.dstack seems to be the quickest way to do this,
        # compared to np.repeat

        if self.convert_to_rgb:
            self.rgb_img = np.dstack([self.img] * 3)

        logging.debug("Image received")
        self.clear_bytes_in_buffer(0, msg_end_idx + 1)

        valid_frame = True
        return valid_frame

    def get_frame(self):
        """
        Get the next frame from the BK5000.
        """
        self.valid_frame = False
        while not self.valid_frame:
            self.minimum_size = self.image_size[0] * self.image_size[1] + 22

            while len(self.buffer) < self.minimum_size:
                self.buffer.extend(self.socket.recv(self.minimum_size))

            valid_frame = self.receive_image()

            if valid_frame:
                self.valid_frame = True

            else:
                self.buffer.extend(self.socket.recv(self.packet_size))


class BKpyIGTLink:
    """ Send BK data over OpenIGTLink. """
    def __init__(self, TCP_IP='128.16.0.3', TCP_PORT=7915, TIMEOUT=5, FPS=25):

        logging.info("Creating BKpyIGTLink connection")
        self.bk5000 = BK5000(TIMEOUT, FPS)
        self.bk5000.connect_to_host(TCP_IP, TCP_PORT)

        self.igtlink_server = PyIGTLink(localServer=True)
        self.active = True
        logging.info("Created BKpyIGTLink connection")


    def start(self):
        """ Start acquisiton/streaming. """

        logging.info("Starting BKpyIGTLink.")
        self.bk5000.query_win_size()
        self.bk5000.start_streaming()

        while self.active:
            if self.igtlink_server.is_connected():
                self.bk5000.get_frame()

                image_message = ImageMessage(self.bk5000.img)
                self.igtlink_server.add_message_to_send_queue(image_message)

    def stop(self):
        """ Stop acquisition/streaming."""
        self.active = False

class BKOpenCV:
    """ Display BK data using OpenCV."""
    #pylint:disable=no-member, invalid-name, import-error

    def __init__(self, TCP_IP='128.16.0.3', TCP_PORT=7915, TIMEOUT=5, FPS=25):
        self.bk5000 = BK5000(TIMEOUT, FPS)
        self.bk5000.connect_to_host(TCP_IP, TCP_PORT)

    def start(self):
        """ Start acquisiton/streaming. """

        self.bk5000.query_win_size()
        self.bk5000.start_streaming()

        while True:
            self.bk5000.get_frame()
            cv2.imshow('a', self.bk5000.img)
            cv2.waitKey(1)

def main():
    """ Entry point for OpenCV/pyIGTLink. """

    # OpenCV or PyIGTLink can be selected from command line
    # 'python bk5000.py' without any arguments wll run openCV
    # adding any argument will use IGTLink instead e.g.
    # 'python bk5000.py 1'

    if len(sys.argv) > 1:
        bk_igtlink = BKpyIGTLink()
        bk_igtlink.start()

    else:
        bk_opencv = BKOpenCV()
        bk_opencv.start()

if __name__ == "__main__":
    main()
