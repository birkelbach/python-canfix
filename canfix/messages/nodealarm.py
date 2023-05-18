#!/usr/bin/env python

#  CAN-FIX Protocol Module - An Open Source Module that abstracts communication
#  with the CAN-FIX Aviation Protocol
#  Copyright (c) 2012 Phil Birkelbach
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import can


class NodeAlarm(object):
    """Represents a Node Alarm"""
    def __init__(self, msg=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.data = []
        self.timestamp = 0.0

    def setMessage(self, msg):
        self.node = msg.arbitration_id
        if len(msg.data) < 2:
            raise ValueError("Node Alarm message missing alarm code")
        self.timestamp = msg.timestamp
        self.alarm = msg.data[0] + msg.data[1]*256
        self.data = msg.data[2:]
        self.data.extend(bytearray(max(0, 5-len(self.data)))) # Pad data with zeros

    def getMessage(self):
        msg = can.Message(is_extended_id=False)
        msg.arbitration_id = self.node
        msg.data.append(int(self.alarm % 256))
        msg.data.append(int(self.alarm / 256))
        for each in self.data:
            msg.data.append(each)
        return msg

    msg = property(getMessage, setMessage)

    def __str__(self):
        s = "[" + str(self.node) + "] Node Alarm " + str(self.alarm) + " Data "
        s += ''.join(format(x, '02X') for x in self.data)
        return s
