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


class NodeConfigurationSet(NodeSpecific):
    def __init__(self, msg=None, key=None, value=None, datatype=None, multiplier=1.0):
        self.multiplier = multiplier
        self.datatype = datatype
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x09
            self.sendNode = None
            self.msgType = MSG_RESPONSE
            self.errorCode = 0
            self.key = key
            if value != None:
                self.value = value

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        if msg.dlc == 3:
            self.msgType = MSG_RESPONSE
            if msg.data[2] == 0x00:
                self.status = MSG_SUCCESS
                self.errorCode = msg.data[2]
            else:
                self.errorCode = msg.data[2]
                self.status = MSG_FAIL
        else:
            self.msgType = MSG_REQUEST
            if self.datatype is not None:
                try:
                    ts = utils.getTypeSize(self.datatype)
                except KeyError:
                    ts = None
                    if ts:
                        if msg.dlc != (3 + ts):
                            raise MsgSizeError("Message size is incorrect")
            if msg.dlc < 4:
                raise MsgSizeError("Message size is incorrect")

            self.key = (msg.data[3] * 256) + msg.data[2]
            self.valueData = msg.data[4:]

        self.controlCode = msg.data[0]
        assert self.controlCode == 0x09
        self.destNode = msg.data[1]

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + self.start_id, is_extended_id=False)
        msg.data = self.data
        msg.dlc = len(msg.data)
        return msg

    msg = property(getMessage, setMessage)

    def setKey(self, key):
        if key == None:
            self.__key = None
            return
        if key < 0 or key > 65535:
            raise ValueError("Key must be between 0 and 65535")
        self.__key = key
        self.msgType = MSG_REQUEST

    def getKey(self):
        return self.__key

    key = property(getKey, setKey)

    def getData(self):
        data = bytearray([])
        data.append(self.controlCode)
        data.append(self.destNode)
        if self.msgType == MSG_REQUEST:
            data.append(self.__key % 256)
            data.append(self.__key >> 8)
            data.extend(self.valueData)
        else:
            data.append(self.errorCode)
        return data

    data = property(getData)

    def setValue(self, value):
        if self.datatype == None:
            raise TypeMissingError("Node Configuration data type is not set")
        self.valueData = utils.setValue(self.datatype, value, self.multiplier)
        self.msgType = MSG_REQUEST

    def getValue(self):
        return utils.getValue(self.datatype, self.valueData, self.multiplier)

    value = property(getValue, setValue)

    def __str__(self):
        s = "[" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "] "
        s += self.codes[self.controlCode]
        return s


class NodeConfigurationQuery(NodeSpecific):
    def __init__(self, msg=None, key=None, value=None, datatype=None, multiplier=1.0):
        self.multiplier = multiplier
        self.datatype = datatype

        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x0A
            self.sendNode = None
            self.destNode = None
            self.key = key
            self.value = value
            #self.rawdata = bytearray([]*5)

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        if msg.dlc < 3:
            raise MsgSizeError("Message size is incorrect")

        self.controlCode = msg.data[0]
        assert self.controlCode == 0x0A
        self.destNode = msg.data[1]
        self.rawdata = msg.data[2:]

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + self.start_id, is_extended_id=False)
        msg.data = self.data
        msg.dlc = len(msg.data)
        return msg

    msg = property(getMessage, setMessage)

    def setKey(self, key):
        if key is None:
            return
        if key < 0 or key > 65535:
            raise ValueError("Key must be between 0 and 65535")
        self.rawdata = bytearray([key % 256, key >> 8])

    def getKey(self):
        return (self.rawdata[1] * 256) + self.rawdata[0]

    key = property(getKey, setKey)

    def getData(self):
        data = bytearray([])
        data.append(self.controlCode)
        data.append(self.destNode)
        data.extend(self.rawdata)
        return data

    data = property(getData)

    def setValue(self, value):
        if value is None:
            return
        if self.datatype == None:
            raise TypeMissingError("Node Configuration data type is not set")
        x = utils.setValue(self.datatype, value, self.multiplier)
        self.rawdata = bytearray([0x00])
        self.rawdata.extend(x)

    def getValue(self):
        if self.datatype == None:
            raise TypeMissingError("Node Status data type is not set")
        return utils.getValue(self.datatype, self.rawdata[1:], self.multiplier)

    value = property(getValue, setValue)

    def setError(self, error):
        if error:
            # If we have an error we don't send any data so
            # this truncates the rawdata
            self.rawdata = bytearray([error % 256])
        else:
            self.rawdata[0] = 0x00

    def getError(self):
        return self.rawdata[0]

    error = property(getError, setError)

    def __str__(self):
        s = "[" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "] "
        s += self.codes[self.controlCode]
        return s
