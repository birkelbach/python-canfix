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
from .. import utils

start_id = 0x6E0

class NodeSpecific(object):
    """Represents a generic Node Specific Message"""
    codes = ["Node Identification", "Bit Rate Set", "Node ID Set", "Disable Parameter",
             "Enable Parameter", "Node Report", "Node Status", "Update Firmware",
             "Connection Request", "Node Configuration Set", "Node Configuration Query",
             "Node Description", "Parameter Set 0", "Parameter Set 32", "Parameter Set 64",
             "Parameter Set 96", "Parameter Set 128", "Parameter Set 160", "Parameter Set 192",
             "Parameter Set 224"]

    def __init__(self, msg=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0
            self.data = bytearray([])

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - start_id
        self.controlCode = msg.data[0]
        #self.destNode = msg.data[1]
        self.data = msg.data[1:]

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + start_id, extended_id=False)
        msg.data.append(self.controlCode)
        #msg.data.append(self.destNode)
        for each in self.data:
            msg.data.append(each)
        msg.dlc = len(msg.data)
        return msg

    msg = property(getMessage, setMessage)

    def getParameterID(self):
        """This is a convenience function that assembles and returns
            the parameter id for Disable/Enable Parameter messages"""
        return (data[1] << 8) + data[0]

    def __str__(self):
        s = "[{}] ".format(str(self.sendNode))
        try:
            s += self.codes[self.controlCode]
        except IndexError:
            if self.controlCode < 128:
                s += "Reserved NSM "
            else:
                s += "User Defined NSM "
            s += str(self.controlCode)
        for each in self.data:
            s += " 0x{:02x}".format(each)
            #s += hex(each)
        return s


class NodeIdentification(NodeSpecific):
    def __init__(self, msg=None, device=None, fwrev=None, model=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x00
            self.msgType = MSG_REQUEST
            self.sendNode = None
            self.destNode = None
            if device is not None: self.device = device
            if fwrev is not None: self.fwrev = fwrev
            if model is not None: self.model = model

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x00
        self.destNode = msg.data[1]
        if msg.dlc == 2:
            self.msgType = MSG_REQUEST
        elif msg.dlc == 8:
            self.msgType = MSG_RESPONSE
            self.device = msg.data[3]
            self.fwrev = msg.data[4]
            self.model = msg.data[5] + (msg.data[6]<<8) + (msg.data[7]<<16)
        else:
            raise MsgSizeError("Message size is incorrect")

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + start_id, extended_id=False)
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
        if device > 255 or device < 0:
            raise ValueError("Device ID must be between 0 and 255")
        else:
            self.__device = device
            self.msgType = MSG_RESPONSE

    def getDevice(self):
        return self.__device

    device = property(getDevice, setDevice)

    def setFwrev(self, fwrev):
        if fwrev > 255 or fwrev < 0:
            raise ValueError("Firmware Revision must be between 0 and 255")
        else:
            self.__fwrev = fwrev
            self.msgType = MSG_RESPONSE


    def getFwrev(self):
        return self.__fwrev

    fwrev = property(getFwrev, setFwrev)

    def setModel(self, model):
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
        s += ": device={}".format(self.device)
        s += ", fwrev={}".format(self.fwrev)
        s += ", model={}".format(self.model)
        return s


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
        self.sendNode = msg.arbitration_id - start_id
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
        msg = can.Message(arbitration_id=self.sendNode + start_id, extended_id=False)
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


class NodeIDSet(NodeSpecific):
    def __init__(self, msg=None, newNode=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x02
            self.msgType = MSG_RESPONSE
            self.sendNode = None
            self.destNode = None
            if newNode is not None: self.newNode = newNode

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x02
        self.destNode = msg.data[1]

        if msg.dlc == 3:
            if msg.data[2] == 0x00:
                self.msgType = MSG_RESPONSE
            else:
                self.msgType = MSG_REQUEST
                self.newNode = msg.data[2]
        else:
            raise MsgSizeError("Message size is incorrect")

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + start_id, extended_id=False)
        msg.data = self.data
        msg.dlc = len(msg.data)
        return msg

    msg = property(getMessage, setMessage)

    def getData(self):
        data = bytearray([])
        data.append(self.controlCode)
        data.append(self.destNode)
        if self.msgType == MSG_RESPONSE:
            data.append(0x00)
        elif self.msgType == MSG_REQUEST:
            data.append(self.newNode)
        return data

    data = property(getData)

    def setNewNode(self, newNode):
        if newNode >= 1 and newNode <= 255:
            self.__newNode = newNode
        else:
            raise ValueError("Invalid Node Number Given")
        self.msgType = MSG_REQUEST

    def getNewNode(self):
        return self.__newNode

    newNode = property(getNewNode, setNewNode)

    def __str__(self):
        s = "[" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "] "
        s += self.codes[self.controlCode]
        if self.msgType == MSG_REQUEST:
            s += ": request new node id={}".format(self.newNode)
        else:
            s += ": Success Response"
        return s


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
        self.sendNode = msg.arbitration_id - start_id
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
        msg = can.Message(arbitration_id=self.sendNode + start_id, extended_id=False)
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
        self.sendNode = msg.arbitration_id - start_id
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


class NodeReport(NodeSpecific):
    def __init__(self, msg=None, newNode=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = 0x05
            self.sendNode = None
            self.destNode = None

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x05
        self.destNode = msg.data[1]

        if msg.dlc != 2:
            raise MsgSizeError("Message size is incorrect")

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + start_id, extended_id=False)
        msg.data = self.data
        msg.dlc = len(msg.data)
        return msg

    msg = property(getMessage, setMessage)

    def getData(self):
        data = bytearray([])
        data.append(self.controlCode)
        data.append(self.destNode)
        return data

    data = property(getData)

    def __str__(self):
        s = "[" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "] "
        s += self.codes[self.controlCode]
        return s


class NodeStatus(NodeSpecific):
    # These are the defined types in the protocol.  The parameter would be
    # used to index this list.  For others the type would have to be set before
    # the value accessed.
    knownTypes = (("WORD",1), ("INT",0.1), ("UDINT",1), ("UDINT",1), ("INT",0.1), ("UDINT",1))
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
        self.sendNode = msg.arbitration_id - start_id
        self.controlCode = msg.data[0]
        assert self.controlCode == 0x06
        self.parameter = (msg.data[2] * 256) + msg.data[1]
        self.valueData = msg.data[3:]
        # TODO: Re-enable this check once getTypeSize can deal with compound data typesl
        # try:
        #     ts = utils.getTypeSize(self.type)
        # except KeyError:
        #     ts = None
        # if ts:
        #     if msg.dlc != (3 + ts):
        #         raise MsgSizeError("Message size is incorrect")
        if msg.dlc < 3:
            raise MsgSizeError("Message size is incorrect")

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + start_id, extended_id=False)
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
            self.type = self.knownTypes[self.__parameter][0]
            self.multiplier = self.knownTypes[self.__parameter][1]
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
        s = "[" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "] "
        s += self.codes[self.controlCode]
        return s
