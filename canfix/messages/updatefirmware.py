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

class UpdateFirmware(NodeSpecific):
    def __init__(self, msg=None, node=None, verification=None, channel=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x07
            self.msgType = MSG_RESPONSE
            self.sendNode = None
            self.destNode = node
            self.errorCode = 0x00
            if verification is not None:
                self.__verification = verification
            else:
                self.__verification = None
            if channel is not None: self.channel = channel

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x07
        self.destNode = msg.data[1]

        if msg.dlc == 3:
            self.msgType = MSG_RESPONSE
            self.errorCode = msg.data[2]
            if self.errorCode == 0x00:
                self.status = MSG_SUCCESS
            else:
                self.status = MSG_FAIL
        elif msg.dlc == 5:
            self.msgType = MSG_REQUEST
            self.verification = msg.data[2] + (msg.data[3]<<8)
            self.channel = msg.data[4]
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
        if self.msgType == MSG_RESPONSE:
            data.append(self.errorCode)
        elif self.msgType == MSG_REQUEST:
            data.append(self.verification % 256)
            data.append(self.verification >> 8)
            data.append(self.channel)
        return data

    data = property(getData)

    def setVerification(self, verification):
        if verification >= 1 and verification <= 0xFFFF:
            self.__verification = verification
        else:
            raise ValueError("Invalid Verification Code Given")
        self.msgType = MSG_REQUEST

    def getVerification(self):
        return self.__verification

    verification = property(getVerification, setVerification)

    def setChannel(self, channel):
        if channel <0 or channel > 15:
            raise ValueError("Invalid Channel Given")
        self.__channel = channel
        self.msgType = MSG_REQUEST

    def getChannel(self):
        return self.__channel

    channel = property(getChannel, setChannel)

    def setErrorCode(self, errorCode):
        if errorCode <0 or errorCode > 255:
            raise ValueError("Invalid Error Given")
        self.__error = errorCode
        self.msgType = MSG_RESPONSE
        if self.__error == 0x00:
            self.status = MSG_SUCCESS
        else:
            self.status = MSG_FAIL

    def getErrorCode(self):
        return self.__error

    errorCode = property(getErrorCode, setErrorCode)

    def __str__(self):
        s = "[" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "] "
        s += self.codes[self.controlCode]
        if self.msgType == MSG_REQUEST:
            s += ": Verification Code={}".format(self.verification)
            s += ": Channel={}".format(self.channel)
        else:
            if self.errorCode:
                s += ": Error Response, Code = {}".format(self.errorCode)
            else:
                s += ": Success Response"
        return s
