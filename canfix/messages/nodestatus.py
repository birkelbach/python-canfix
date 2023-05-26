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


class NodeStatus(NodeSpecific):
    # These are the defined types in the protocol.  The parameter would be
    # used to index this list.  For others the type would have to be set before
    # the value accessed.
    knownTypes = (("Status","WORD",1),
                  ("Unit Temperature", "INT",0.1),
                  ("Supply Voltage","INT",0.1),
                  ("CAN Transmit Frame Count", "UDINT",1),
                  ("CAN Receive Frame Count", "UDINT",1),
                  ("CAN Transmit Error Count", "UDINT",1),
                  ("CAN Transmit Error Count", "UDINT",1),
                  ("CAN Receive Overrun Count", "UDINT",1),
                  ("Serial Number", "UDINT",1))
    def __init__(self, msg=None, parameter=None, value=None, datatype=None, multiplier=1.0):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x06
            self.sendNode = None
            self.parameter = parameter
            if value != None:
                self.value = value

        self.multiplier = multiplier
        if datatype != None:
            self.type =  datatype


    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x06
        self.parameter = (msg.data[2] * 256) + msg.data[1]
        self.valueData = msg.data[3:]
        try:
            ts = utils.getTypeSize(self.type)
        except KeyError:
            ts = None
        if ts:
            if msg.dlc != (3 + ts):
                raise MsgSizeError("Message size is incorrect - {}".format(msg))
        if msg.dlc < 3:
            raise MsgSizeError("Message size is incorrect")

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + self.start_id, is_extended_id=False)
        msg.data = self.data
        msg.dlc = len(msg.data)
        return msg

    msg = property(getMessage, setMessage)

    def setParameter(self, parameter):
        if parameter == None:
            self.__parameter = None
            return
        if parameter < 0 or parameter > 65535:
            raise ValueError("Paremeter Type must be between 0 and 65535")
        self.__parameter = parameter
        if self.__parameter < len(self.knownTypes):
            self.type = self.knownTypes[self.__parameter][1]
            self.multiplier = self.knownTypes[self.__parameter][2]
        else:
            self.type = None # This'll cause an error somewhere.
            self.multiplier = 1

    def getParameter(self):
        return self.__parameter

    parameter = property(getParameter, setParameter)

    def getData(self):
        data = bytearray([])
        data.append(self.controlCode)
        data.append(self.__parameter % 256)
        data.append(self.__parameter >> 8)
        data.extend(self.valueData)
        return data

    data = property(getData)

    def setValue(self, value):
        if self.type == None:
            raise TypeMissingError("Node Status data type is not set")
        self.valueData = utils.setValue(self.type, value, self.multiplier)

    def getValue(self):
        return utils.getValue(self.type, self.valueData, self.multiplier)

    value = property(getValue, setValue)

    def __str__(self):
        s = "[" + str(self.sendNode) + "] "
        s += self.codes[self.controlCode]
        if self.__parameter < len(self.knownTypes):
            if self.__parameter == 0 :
                if self.value == [False]*16:
                    s += ": {} GOOD".format(self.knownTypes[self.__parameter][0])
                else:
                    errors = ""
                    for each in self.value:
                        if each:
                            errors += '1'
                        else:
                            errors += '0'
                    s += ": {} ERROR {}".format(self.knownTypes[self.__parameter][0], errors)
            else:
                s += ": {} {}".format(self.knownTypes[self.__parameter][0], self.value)
        else:
            s+= ": Parameter {} {}".format(self.__parameter, self.data)
        return s
