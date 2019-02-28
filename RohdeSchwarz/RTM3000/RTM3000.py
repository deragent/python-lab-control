import socket
import time
import sys

import numpy as np

class RTM3000:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

        self._openSocket()

    def __del__(self):
        self._closeSocket()

    def _openSocket(self):
        try:
            #create an AF_INET, STREAM socket (TCP)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print('Failed to create socket.')
            sys.exit();

        try:
            #Connect to remote server
            self.sock.connect((self.ip , self.port))
        except socket.error:
            print('failed to connect to ip ' + remote_ip)

    def _closeSocket(self):
        self.sock.close()
        time.sleep(.300)

    def close(self):
        self._closeSocket()


    def query(self, cmd, resp=False, len=4096):
        """
        Sends a command to the instrument and receives data if needed.

        The cmd string is encoded to bytes and a NEWLINE is appended.
        This function waits to receive data in return if resp=True is passed as an argument.
        The returned data is decoded into a string and the NEWLINE is stripped.
        """
        try:
            #Send cmd string
            self.sock.sendall(cmd.encode() + b'\n')
            time.sleep(0.2)
        except socket.error:
            #Send failed
            print ('Send failed')
            sys.exit()

        if resp:
            reply = self.sock.recv(int(len))
            return reply.decode().strip('\n')
        else:
            return True

    def receiveBinary(self, cmd):
        """
        Sends a SCPI command and receives the binary format data in response.

        The cmd sent must make the device return binary data in the standard SCPI format
            #NAA.AAddd...ddd

        # Is literlly the character '#'
        N           is the number of 'A' bytes
        AA..AA      denote the number of bytes in the payload
        dddd..dddd  is the payload of length AA..AA
        """

        self.query(cmd)

        primer = self.sock.recv(2).decode()
        N = int(primer[1])
        length = int(self.sock.recv(N).decode())

        data = b''

        while len(data) < length+1:
            data = data + self.sock.recv(4096)

        data = data[0:length]

        return data


    ## -----------------------------------------

    def waitForTrigger(self):
        """
        Sets the RTM to single trigger mode, and waits for a trigger to happen.
        """

        return int(self.query("SING;*OPC?", True))


    def downloadChannel(self, ch):
        """
        Download the data for a single channel.

        This function first reads the header information (X and Y scaling and offset) and then downloads the data in binary format.
        The X and Y scaling and offset are applied to the downloaded binary data and the time and values arrays are returned.
        """
        if ch not in [1, 2, 3, 4]:
            return None

        xstart, xstop, len, _ = [float(v) for v in self.query("CHAN%i:DATA:HEAD?"%(ch), True).split(',')]
        yres = float(self.query("CHAN%i:DATA:YRES?"%(ch), True))
        yor = float(self.query("CHAN%i:DATA:YOR?"%(ch), True))
        xor = float(self.query("CHAN%i:DATA:XOR?"%(ch), True))
        xinc = float(self.query("CHAN%i:DATA:XINC?"%(ch), True))

        # Set the data format to binary unsigned int16 and set MSB bit order
        self.query("FORM UINT,16")
        self.query("FORM:BORDER MSB")

        yinc = float(self.query("CHAN%i:DATA:yinc?"%(ch), True))

        data_raw = self.receiveBinary("CHAN%i:DATA?"%(ch))

        # Convert the raw binary data to an array of unsigned int16
        dt = np.dtype(np.uint16)
        dt = dt.newbyteorder('>')
        data = np.frombuffer(data_raw, dtype=dt)

        # Calculate the actual values
        time = xinc*np.arange(0, len) + xor
        values = yor + yinc*data

        return (time, values)
