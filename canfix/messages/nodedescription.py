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
from ..globals import *
from .. import utils
from .nodespecific import NodeSpecific

class NodeDescription(NodeSpecific):
    def __init__(self, msg=None, packetnumber=0x00, chars=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x0B
            self.sendNode = None
            self.destNode = None
            self.packetnumber = 0x00
            if chars:
                self.chars = bytearray(chars)
            else:
                self.chars = bytearray([0x00]*4)

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x0B
        self.destNode = msg.data[1]
        self.packetnumber = msg.data[3] * 256 + msg.data[2]
        self.chars = msg.data[4:]

        if msg.dlc < 8:
            raise MsgSizeError("Message size is incorrect")

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + self.start_id, is_extended_id=False)
        msg.data = self.data
        msg.dlc = len(msg.data)
        return msg

    msg = property(getMessage, setMessage)

    def getData(self):
        data = bytearray([])
        data.append(self.controlCode)
        data.append(self.destNode)
        data.append(self.packetnumber % 265)
        data.append(self.packetnumber >> 8)
        data.extend(bytearray(self.chars[0:4], 'utf8'))
        return data

    data = property(getData)

    def __str__(self):
        s = "[" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "] "
        s += self.codes[self.controlCode]
        return s
