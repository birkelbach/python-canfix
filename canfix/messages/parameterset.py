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
from ..protocol import parameters, getParameterByName
from .nodespecific import NodeSpecific


class ParameterSet(NodeSpecific):
    def __init__(self, msg=None, parameter=None, value=None, datatype=None, multiplier=None, index=0):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x0B
            self.sendNode = None
            self.parameter = parameter
            self.index = index
        # If this is a predefined parameter we can automatically set the
        # multiplier and the datatype
        if self.parameter in parameters:
            self.multiplier = parameters[self.parameter].multiplier
            self.type = parameters[self.parameter].type

        # If we really, really want to set these then we can
        if multiplier != None:
            self.multiplier = multiplier
        if datatype != None:
            self.type =  datatype
        if value != None:
            self.value = value


    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        self.controlCode = msg.data[0]
        assert self.controlCode >= 0x0C
        assert self.controlCode <= 0x13
        self.parameter = ((msg.data[2] * 256) + msg.data[1]) & 0x07FF
        self.index = (self.controlCode - 0x0C)*32 + (msg.data[2] >> 3)
        self.valueData = msg.data[3:]
        try:
            ts = utils.getTypeSize(self.type)
        except KeyError:
            ts = None
        if ts:
            if msg.dlc != (3 + ts):
                raise MsgSizeError("Message size is incorrect")
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
        if type(parameter) == int:
            if parameter < 256 or parameter > 1759:
                raise ValueError("Paremeter Type must be between 256 and 1759")
            self.__parameter = parameter
        else:
            p = getParameterByName(parameter)
            self.__parameter = p.id
        self.type = parameters[self.__parameter].type
        self.multiplier = parameters[self.__parameter].multiplier

    def getParameter(self):
        return self.__parameter

    parameter = property(getParameter, setParameter)

    def setIndex(self, index):
        if index < 0 or index >= 256:
            raise ValueError("Index must be between 0 and 255")
        self.__index = index
        self.controlCode = (index // 32) + 0x0C


    def getIndex(self):
        return self.__index

    index = property(getIndex, setIndex)

    def getData(self):
        data = bytearray([])
        data.append(self.controlCode)
        x = (self.index % 32) << 11 | self.parameter
        data.append(x % 256)
        data.append(x >> 8)
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
        s += self.codes[self.controlCode] + " "
        if self.parameter in parameters:
            s += parameters[self.parameter].name
        s += "({})".format(hex(self.parameter))
        s += " = {}".format(self.value)
        return s
