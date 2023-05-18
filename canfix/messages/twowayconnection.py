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


class TwoWayConnection(NodeSpecific):
    def __init__(self, msg=None, node=None, connectionType=0x0000, channel=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x08
            self.msgType = MSG_RESPONSE
            self.sendNode = None
            self.destNode = None
            if channel is not None: self.channel = channel
            if connectionType is not None: self.connectionType = connectionType

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x08
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
            self.channel = msg.data[2]
            self.connectionType = msg.data[3] + (msg.data[4]<<8)
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
            data.append(self.channel)
            data.append(self.connectionType % 256)
            data.append(self.connectionType >> 8)
        return data

    data = property(getData)

    def setConnectionType(self, connectionType):
        if connectionType >= 0 and connectionType <= 0xFFFF:
            self.__connectionType = connectionType
        else:
            raise ValueError("Invalid Connection Type Given")
        self.msgType = MSG_REQUEST

    def getConnectionType(self):
        return self.__connectionType

    connectionType = property(getConnectionType, setConnectionType)

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
            s += ": Connection Type={}".format(self.connectionType)
            s += ": Channel={}".format(self.channel)
        else:
            if self.errorCode:
                s += ": Error Response, Code = {}".format(self.errorCode)
            else:
                s += ": Success Response"
        return s
