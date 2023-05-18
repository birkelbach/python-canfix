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
from .nodespecific import NodeSpecific

class BitRateSet(NodeSpecific):
    def __init__(self, msg=None, bitrate=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x01
            self.msgType = MSG_RESPONSE
            self.status = MSG_SUCCESS
            self.sendNode = None
            self.destNode = None
            if bitrate is not None: self.bitrate = bitrate

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x01
        self.destNode = msg.data[1]

        if msg.dlc == 2:
            self.msgType = MSG_RESPONSE
            self.status = MSG_SUCCESS
        elif msg.dlc == 3:
            if msg.data[2] == 0xFF:
                self.msgType = MSG_RESPONSE
                self.status = MSG_FAIL
            else:
                self.msgType = MSG_REQUEST
                self.bitrate = msg.data[2]
        else:
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
        if self.msgType == MSG_RESPONSE and self.status == MSG_FAIL:
            data.append(0xFF)
        elif self.msgType == MSG_REQUEST:
            data.append(self.bitrate)
        return data

    data = property(getData)

    bitrates = {125:1, 250:2, 500:3, 1000:4}

    def setBitRate(self, bitrate):
        if bitrate >= 1 and bitrate <= 4:
            self.__bitrate = bitrate
        elif bitrate in self.bitrates:
            self.__bitrate = self.bitrates[bitrate]
        else:
            raise ValueError("Invalid Bit Rate Given")
        self.msgType = MSG_REQUEST

    def getBitRate(self):
        return self.__bitrate

    bitrate = property(getBitRate, setBitRate)

    def __str__(self):
        s = "[" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "] "
        s += self.codes[self.controlCode]
        if self.msgType == MSG_REQUEST:
            for each in self.bitrates:
                if self.bitrates[each] == self.bitrate:
                    b = each
                    break
            s += ": request bitrate={}kbps".format(b)
        else:
            if self.status == MSG_SUCCESS:
                s += ": Success Response"
            elif self.status == MSG_FAIL:
                s += ": Failure Response"
        return s
