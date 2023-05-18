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
from ..protocol import getParameterByName
from .nodespecific import NodeSpecific


class DisableParameter(NodeSpecific):
    def __init__(self, msg=None, identifier=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x03
            self.msgType = MSG_RESPONSE
            self.sendNode = None
            self.destNode = None
            if identifier is not None: self.identifier = identifier

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x03
        self.destNode = msg.data[1]

        if msg.dlc == 3:
            self.msgType = MSG_RESPONSE
            if msg.data[2] == 0x00:
                self.status = MSG_SUCCESS
            elif msg.data[2] == 0x01:
                self.status = MSG_FAIL
            else:
                raise ValueError("Unknown Error Code {}".format(msg.data[2]))
        elif msg.dlc == 4:
            self.identifier = msg.data[2] + (msg.data[3]<<8)
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
            if self.status == MSG_SUCCESS:
                data.append(0x00)
            else:
                data.append(0x01)
        elif self.msgType == MSG_REQUEST:
            data.append(self.identifier % 256)
            data.append(self.identifier >> 8)
        return data

    data = property(getData)

    def setIdentifier(self, identifier):
        if isinstance(identifier, str):
            x = getParameterByName(identifier)
            if x:
                identifier = x.id
            else:
                identifier = 0
        if identifier >= 256 and identifier <= 1759:
            self.__identifier = identifier
        else:
            raise ValueError("Invalid identifier Given")
        self.msgType = MSG_REQUEST

    def getIdentifier(self):
        return self.__identifier

    identifier = property(getIdentifier, setIdentifier)

    def __str__(self):
        s = "[" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "] "
        s += self.codes[self.controlCode]
        if self.msgType == MSG_REQUEST:
            s += ": request identifier={}".format(self.identifier)
        else:
            if self.status == MSG_SUCCESS:
                s += ": Success Response"
            else:
                s += ": Failure Response"
        return s


# We can use most of the DisableParameter code only the ControlCode is different
class EnableParameter(DisableParameter):
    def __init__(self, msg=None, identifier=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x04
            self.msgType = MSG_RESPONSE
            self.sendNode = None
            self.destNode = None
            if identifier is not None: self.identifier = identifier

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x04
        self.destNode = msg.data[1]

        if msg.dlc == 3:
            self.msgType = MSG_RESPONSE
            if msg.data[2] == 0x00:
                self.status = MSG_SUCCESS
            elif msg.data[2] == 0x01:
                self.status = MSG_FAIL
            else:
                raise ValueError("Unknown Error Code {}".format(msg.data[2]))
        elif msg.dlc == 4:
            self.identifier = msg.data[2] + (msg.data[3]<<8)
        else:
            raise MsgSizeError("Message size is incorrect")
