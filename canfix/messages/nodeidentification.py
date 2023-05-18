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

class NodeIdentification(NodeSpecific):
    def __init__(self, msg=None, device=None, fwrev=None, model=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x00
            self.msgType = MSG_REQUEST
            self.sendNode = None
            self.destNode = None
            self.device = device
            self.fwrev = fwrev
            self.model = model

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x00
        if msg.dlc == 2:
            self.destNode = msg.data[1]
            self.msgType = MSG_REQUEST
        elif msg.dlc == 8:
            self.destNode = msg.data[1]
            self.msgType = MSG_RESPONSE
            self.device = msg.data[3]
            self.fwrev = msg.data[4]
            self.model = msg.data[5] + (msg.data[6]<<8) + (msg.data[7]<<16)
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
            data.append(0x01) # CAN-FIX Specification Revision
            data.append(self.device)
            data.append(self.fwrev)
            data.extend([self.model & 0x0000FF, (self.model & 0x00FF00) >> 8, (self.model & 0xFF0000) >> 16])

        return data

    data = property(getData)

    def setDevice(self, device):
        if device is None:
            self.__device = None
        else:
            if device > 255 or device < 0:
                raise ValueError("Device ID must be between 0 and 255")
            else:
                self.__device = device
                self.msgType = MSG_RESPONSE

    def getDevice(self):
        return self.__device

    device = property(getDevice, setDevice)

    def setFwrev(self, fwrev):
        if fwrev is None:
            self.__fwrev = None
        else:
            if fwrev > 255 or fwrev < 0:
                raise ValueError("Firmware Revision must be between 0 and 255")
            else:
                self.__fwrev = fwrev
                self.msgType = MSG_RESPONSE


    def getFwrev(self):
        return self.__fwrev

    fwrev = property(getFwrev, setFwrev)

    def setModel(self, model):
        if model is None:
            self.__model = None
        else:
            if model < 0 or model > 0xFFFFFF:
                raise ValueError("Model must be between 0 and 0xFFFFFF")
            else:
                self.__model = model
                self.msgType = MSG_RESPONSE

    def getModel(self):
        return self.__model

    model = property(getModel, setModel)

    def __str__(self):
        s = "[" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "] "
        s += self.codes[self.controlCode]
#        s += ": device={}".format(self.device)
#        s += ", fwrev={}".format(self.fwrev)
#        s += ", model={}".format(self.model)
        return s
