#!/usr/bin/env python
#
# Simple test script for EBAM PLUS serial port connection
#
# Patrick O'Keeffe | WSU Laboratory for Atmospheric Research 2018
#

from __future__ import print_function
import serial
import time
import warnings


class EbamPlus:
    def __init__(self, port):
        """Represents an EBAM Plus aerosol sampler

        Params
        ------
        port : string, required
            Name of serial port device
        """
        self.port = port
        ####connects automatically
        self.cli = serial.Serial(self.port, timeout=5.0)
        ### future: automatically populate w/ EBAM unit data

    def __enter__(self):
        self.connect()
        return(self)

    def __exit__(self, type, value, traceback):
        self.disconnect()

    def connect(self):
        """Open communications with EBAM Plus unit"""
        if not self.cli.isOpen():
            self.cli.open()

    def disconnect(self):
        """Close communications with EBAM Plus unit"""
        self.cli.close()

    def calc_checksum(self, command):
        """Calculate command checksum

        Per 7500 protocol Rev A document, checksum is 16-bit
        unsigned integer sum of all characters between the
        opening delimter (<Esc>) and the checksum character (*).

        Params
        ------
        command : string
            Raw command with parameters

        Returns
        -------
        integer checksum value
        """
        c = 0
        for letter in command:
            c += ord(letter)
        return( c % 2**16 )

    def eval_checksum(self, resp):
        """Evalute response checksum for validity

        Issues `Warning` if checksum validation fails.

        Params
        ------
        resp : string
            Full response string possibly with multiple lines

        Returns
        -------
        A copy of `resp` with checksums removed, even if validation fails
        """
        copy = ""
        for line in resp.splitlines():
            parts = line.split('*')
            if len(parts) < 2: # blank / no checksum line
                copy += '\n'
            elif not len(parts[0]): # checksum on otherwise blank line
                copy += '\n'
            else:
                recvd = int(parts[1])
                calcd = self.calc_checksum(parts[0])
                if recvd != calcd:
                    warnings.warn("EbamPlus.eval_checksum: validation failed ({}): ".format(calcd), line)
                copy += parts[0]+'\n'
        return copy

    def comp_command(self, command):
        """Send command to EBAM and return unit's reply

        Sent in computer mode with checksum validation. If
        validation fails, a `Warning` is issued.

        Params
        ------
        command : string
            verbatim command with optional parameters

        Returns
        -------
        string : EBAM response
        """
        self.cli.flush()
        chksum = self.calc_checksum(command)
        cmd = '\x1b{}*{}\r'.format(command, chksum)
        print('Sending EBAM Plus command: '+repr(cmd))
        bytes = self.cli.write(cmd)
        res = ''.join(self.cli.readlines()) #subject to port timeout
        validated = self.eval_checksum(res)
        return validated


    def report_settings(self):
        return self.comp_command('1')

    def report_last_data(self, param1=None):
        if param1 is not None:
            cmd = '4 {}'.format(param1)
        else:
            cmd = '4'
        return self.comp_command(cmd)

    def report_alarm_events(self):
        return self.comp_command('7')



### Method 1
"""
with EbamPlus('/dev/ttyUSB0') as ebam:
    print('Requesting settings report...')
    print(ebam.report_settings())
"""

### method 2

ebam = EbamPlus('/dev/ttyUSB0') # connects automatically

print('Requesting latest data...')
print(ebam.report_last_data(4))

