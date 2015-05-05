#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#Coin acceptor handler script
#Copyright (C) 2015 Micha³ Borejszo
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import serial, time, sys, os
from ccTalk import *

def validMessage(message):
    return message.source == target and message.destination == 1

def validResponse(message):
    return validMessage(message) and message.payload.header == 0

def poll(header):
    cc.setPayload(header)
    cc.send()
    for m in parseMessages(ser.read(50)):
        if validResponse(m):
            return m

def pollAndParse(header):
    return poll(header).payload.parsePayload(header)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: %s COM_PATH" % os.path.basename(__file__))
        sys.exit(1)

    portPath = sys.argv[1]
    ser = serial.Serial(portPath, 9600, timeout=0.2)
    cc = ccTalkMessage(io = ser)

    # Coin acceptor address
    if len(sys.argv) == 2:
        target = 2
    else:
        target = int(sys.argv[2])

    # Wait till coin acceptor is online
    print("Waiting for coin acceptor to be online...")
    while True:
        cc.setPayload(254)
        cc.send()
        data = ser.read(50)
        messages = parseMessages(data)
        ok = False
        for m in messages:
            if validResponse(m):
                ok = True
                break
        if ok == True:
            break
        time.sleep(0.2)
    print("Coin acceptor online")

    # Get coin acceptor data
    print "Polling coin acceptor for info..."
    print headerTypes[246], " ", pollAndParse(246)
    print headerTypes[244], " ", pollAndParse(244)
    print headerTypes[241], " ", pollAndParse(241)

    # event/error buffer poll
    while True:
        print pollAndParse(229)
