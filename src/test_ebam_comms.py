#!/usr/bin/env python
#
# Simple test script for EBAM PLUS serial port connection
# Basically, we want to determine if null modem adapter is necessary
#
# Patrick O'Keeffe | WSU Laboratory for Atmospheric Research 2018
#

from __future__ import print_function
import serial
import time

print('Connecting to EBAM PLUS on /dev/ttyUSB0... ', end='')
try:
    with serial.Serial('/dev/ttyUSB0', timeout=3.0) as ebam:
        print('OK')

        print('Entering command mode...')
        ebam.write('\r\r\r') # enter User Comm mode
        time.sleep(0.5)

        # based on Rev B user manual
        print('Querying Model/Part/Revision...')
        ebam.write('RV')

        res = ebam.read(100)
        if (res):
            print('[ OK ] Responded:', res.strip())
        else:
            print('[ ERROR ] No response: query timed out')

except Exception:
    print('Unknown failure')

