#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#Created on Wed May 23 14:49:27 2018

#Retrieves all data from ebam and saves to a csf file

#@author: Marissa

from __future__ import print_function
import serial
import time

def  getEbamLastHour():

    gooddata=0
    lengthchars=2000

    for i in range (0,4):
        print('Connecting to EBAM PLUS on /dev/ttyUSB0... ', end='')
        try:
            with serial.Serial('/dev/ttyUSB0', timeout=3.0) as ebam:
                print('OK')
                print('Entering command mode...')
                ebam.write('\r\r\r') # enter User Comm mode
                time.sleep(0.5)

                print('Getting data...')
                ebam.write('4')         #2 for all data, 3 for new data, 4 for last data 

                res=ebam.read(lengthchars)

                if (res):
                    print('[ OK ] Responded:')
                    print(res)
                else:
                    print('[ ERROR ] No response: query timed out')

        except Exception:
            print('Unknown failure')
        time.sleep(0.5)
        if len(res)>=80:
            gooddata=1
            hourline=res.split("\n",8)[7]
            #print('hourline is:')
            #print(hourline)
            f=open("/tmp/ebam.csv", "w")
            f.write('Time,ConcRT(ug/m3),ConcHR(ug/m3),Flow(lpm),WS(m/s),WD(Deg),AT(C),RH(%),BP(mmHg),FT(C),FRH(%),BV(V),PM,Status\n')
            f.write(hourline)
            f.close()
            break
    print('gooddata =',gooddata)


    return hourline
