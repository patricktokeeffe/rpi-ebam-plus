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
                    warnings.warn("EbamPlus.eval_checksum: validation failed ({}): {}".format(calcd, line))
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
        #print('Sending EBAM Plus command: '+repr(cmd))
        bytes = self.cli.write(cmd)
        res = ''.join(self.cli.readlines()) #subject to port timeout
        validated = self.eval_checksum(res)
        return validated


    def MetRecord_revision(self):
        """Return the MetRecord revision"""
        return self.comp_command('#').lstrip('# ').rstrip()

    def report_settings(self):
        """Return the setting report"""
        return self.comp_command('1').lstrip().rstrip()

    def report_all_data(self):
        """Return all the data"""
        #raise NotImplementedError("Sorry, serial port not recommended for all data")
        # maybe increase timeout size? buffers too?
        return self.comp_command('2')

    def report_new_data(self):
        """Return data since last request"""
        return self.comp_command('3')

    def report_last_data(self, param1=None):
        """Return the last data record.

        Params
        ------
        param1 : {0, -1, *n*, *ts*}, optional
            Optionally specify ~~`0` for all the data records,~~
            -1 for records since last request,
            *n* for last *n* hours where *n* <= 2000, or
            *ts* for data since timestamp where *ts* has format
            `yyyy-MM-dd HH:mm:ss`.
        """
        if param1 == 0:
            raise NotImplementedError("Sorry, serial port not recommended for all data")
            # see `report_all_data()` above
        elif param1 is not None:
            cmd = '4 {}'.format(param1)
        else:
            cmd = '4'
        return self.comp_command(cmd)

    def report_alarms(self):
        """Return all alarm events"""
        return self.comp_command('7').rstrip()

    ## skip clear_data_log(self):

    def date(self):
        """Return the date part of the real time clock (no time)"""
        return self.comp_command('D').lstrip('D ').rstrip()

    ## skip the help menu ('H')

    def k_factor(self):
        """Request the factory K-factor calibration value"""
        return self.comp_command('K').lstrip('K ').rstrip()

    ## skip set_k_factor (K)
    ## skip exit user mode (Q)

    def time(self): # TODO set time
        """Request the time part of the real time clock"""
        return self.comp_command('T').lstrip('T ').rstrip()

    # skip analog_range (AR)
    # skip clear_alarm_log(CA Y)

    def conc_offset(self): # TODO set offset
        """Request the concentration offset"""
        return self.comp_command('CO').lstrip('CO ').rstrip()

    def conc_range(self): # TODO set range
        """Request the concentration range"""
        return self.comp_command('CR').lstrip('CR ').rstrip()

    def conc_type(self): # TODO set type
        """Request the concentration type (actual or standard)"""
        return self.comp_command('CT').lstrip('CT ').rstrip()

    def count_units(self): # TODO set units
        """Request the count unit setting"""
        return self.comp_command('CU').lstrip('CU ').rstrip()

    def descriptor_info(self):
        """Request all the general and header info"""
        # TODO strip "DS" prefixes from each line?
        return self.comp_command('DS')

    def crc(self):
        """Request the instrument descriptor table CRC"""
        return self.comp_command('DSCRC').lstrip('DSCRC ').rstrip()

    def datetime(self):
        """Request the date and time parts of the real time clock"""
        return self.comp_command('DT').lstrip('DT ').rstrip()

    ## skip "ethernet" flow control

    def location(self):
        """Request the location ID"""
        return self.comp_command('ID').lstrip('ID').rstrip()

    ## skip modbus address (MA)
    ## skip network mode (NW)
    ## skip output interval (OI)

    def op_state(self):
        """Request the current operation state"""
        return self.comp_command('OP').lstrip('OP ').rstrip()

    def inlet_type(self):
        """Request the current PM inlet type"""
        return self.comp_command('PM').lstrip('PM ').rstrip()

    ## skip print report (PR)
    ## skip unlock user commands (PW)

    def report_data_header(self):
        """Report data record header"""
        return self.comp_command('QH')

    def last_record(self):
        """Request the instantaneous measurement record"""
        return self.comp_command('RQ')

    ## skip (RS) - alias of (1)

    def report_model_info(self): # TODO params?
        """Request the model number, firmware part number, and revision string"""
        return self.comp_command('RV')

    def serial_baud(self): # TODO set baud rate
        """Request the serial port baud rate"""
        return self.comp_command('SB').lstrip('SB ').rstrip()

    def serial_number(self):
        """Request the serial number"""
        return self.comp_command('SS').lstrip('SS ').rstrip()

    def sample_time(self): # TODO set time
        """Request the sample time"""
        return self.comp_command('ST').lstrip('ST ').rstrip()

    def timestamp_mode(self): # TODO set mode
        """Request the timestamp mode setting"""
        return self.comp_command('TS').lstrip('TS ').rstrip()

    ## skip the per-channel field units get/set (UN)
    ## skip AIRSIS protocol enable setting (AIR)
    ## skip request/set user password (SPW)

    def timezone_offset(self):
        """Request the timezone offset""" # TODO set TZO
        return self.comp_command('TZO').lstrip('TZO ').rstrip()

    ## skip Xmodem record descriptors
    ## skip Xmodem read file

    def background_offset(self): # TODO set background
        """Request the background offset value"""
        return self.comp_command('BKGD').lstrip('BKGD ').rstrip()

    def filter_tmpr_setpoint(self): #TODO set setpoint
        """Request the filter temperature set point"""
        return self.comp_command('FTSP').lstrip('FTSP ').rstrip()

    def span_value(self): # TODO set span
        """Request the span calibration verification value"""
        return self.comp_command('SPAN').lstrip('SPAN ').rstrip()

    ## skip get/set standard tmperature (STDT)
    ## skip repeat DSCRC
    ## skip get/set modem type (MODEM)

    def realtime_period(self): # TODO set period
        """Request the real-time averaging period (minutes)"""
        return self.comp_command('RTPER').lstrip('RTPER ').rstrip()

    ## skip get/set tape advanced pressure (TPRES)
    ## skip Xmodem file CRC (XRDCRC)
    ## skip clock sync mode (CLKSYNC)


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

