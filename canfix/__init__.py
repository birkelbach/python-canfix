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

import struct
import time
import logging
import can
from .protocol import parameters

log = logging.getLogger("canfix")

MSG_REQUEST =  0x01
MSG_RESPONSE = 0x02

class MsgSizeError(Exception):
    pass

class NodeAlarm(object):
    """Represents a Node Alarm"""
    def __init__(self, msg=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.data = []

    def setMessage(self, msg):
        self.node = msg.arbitration_id
        if len(msg.data) < 2:
            raise ValueError("Node Alarm message missing alarm code")
        self.alarm = msg.data[0] + msg.data[1]*256
        self.data = msg.data[2:]
        self.data.extend(bytearray(5-len(self.data))) # Pad data with zeros

    def getMessage(self):
        msg = can.Message(extended_id=False)
        msg.arbitration_id = self.node
        msg.data.append(int(self.alarm % 256))
        msg.data.append(int(self.alarm / 256))
        for each in self.data:
            msg.data.append(each)
        return msg

    msg = property(getMessage, setMessage)

    def __str__(self):
        s = "[" + str(self.node) + "] Node Alarm " + str(self.alarm) + " Data "
        s += ''.join(format(x, '02X') for x in self.data)
        return s


class Parameter(object):
    """Represents a normal parameter update message frame"""
    def __init__(self, msg=None):
        if msg != None and len(msg.data) >= 4:
            log.debug("Creating Parameter with message: {}".format(str(msg)))
            #if len(msg.data) < 4: return None
            self.setMessage(msg)
        else:
            log.debug("Creating Parameter with default values")
            self.__name = ""
            self.__identifier = 0
            self.__failure = False
            self.__quality = False
            self.__annunciate = False
            self.value = 0
            self.index = 0
            self.node = 0
            self.__meta = None
            self.function = 0

    def __parameterData(self, msgID):
        # This function gets the data from the XML file dictionary
        p = parameters[msgID]
        self.__name = p.name
        self.units = p.units
        self.type = p.type
        self.min = p.min
        self.max = p.max
        self.format = p.format
        self.remarks = p.remarks
        self.indexName = p.index
        self.multiplier = p.multiplier
        if self.multiplier == None:
            self.multiplier = 1

    def setIdentifier(self, identifier):
        if identifier in parameters:
            log.debug("Setting parameter id {}".format(identifier))
            self.__msg = can.Message(arbitration_id=identifier, extended_id=False)
        else:
            raise ValueError("Bad Parameter Identifier Given")

        self.__identifier = self.__msg.arbitration_id
        self.__parameterData(self.__msg.arbitration_id)

    def getIdentifier(self):
        return self.__identifier

    identifier = property(getIdentifier, setIdentifier)

    def setName(self, name):
        s = name.upper()
        for i in parameters:
            if parameters[i].name.upper() == s:
                log.debug("Setting parameter id to {}, based on name {}".format(i, name))
                self.__msg = can.Message(arbitration_id=i, extended_id=False)
                self.__identifier = i
                self.__parameterData(self.__msg.arbitration_id)
                return
        raise ValueError("Unknown Parameter Name - {}".format(name))

    def getName(self):
        return self.__name

    name = property(getName, setName)

    def setFailure(self, failure):
        if failure:
            self.function |= 0x04
            self.__failure = True
        else:
            self.function &= ~0x04
            self.__failure = False

    def getFailure(self):
        return self.__failure

    failure = property(getFailure, setFailure)

    def setQuality(self, quality):
        if quality:
            self.function |= 0x02
            self.__quality = True
        else:
            self.function &= ~0x02
            self.__quality = False

    def getQuality(self):
        return self.__quality

    quality = property(getQuality, setQuality)

    def setAnnunciate(self, annunciate):
        if annunciate:
            self.function |= 0x01
            self.__annunciate = True
        else:
            self.function &= ~0x01
            self.__annunciate = False

    def getAnnunciate(self):
        return self.__annunciate

    annunciate = property(getAnnunciate, setAnnunciate)

    def setMeta(self, meta):
        if isinstance(meta, int):
            self.function &= 0x0F
            self.function |= meta << 4
            self.__meta = parameters[self.__msg.arbitration_id].auxdata[meta]
        elif isinstance(meta, str):
            p = parameters[self.__msg.arbitration_id]
            for each in p.auxdata:
                if p.auxdata[each].upper() == meta.upper():
                    self.function &= 0x0F
                    self.function |= each << 4
                    self.__meta = p.auxdata[each] # Get's the case right
        else:
            self.__meta = None

    def getMeta(self):
        return self.__meta

    meta = property(getMeta, setMeta)

    def setMessage(self, msg):
        self.__msg = msg
        p = parameters[msg.arbitration_id]
        self.__identifier = msg.arbitration_id
        self.__parameterData(msg.arbitration_id)
        self.node = msg.data[0]
        self.index = msg.data[1]
        self.function = msg.data[2]
        self.data = bytearray(msg.data[3:])
        if self.function & 0x04:
            self.__failure = True
        else:
            self.__failure = False
        if self.function & 0x02:
            self.quality = True
        else:
            self.quality = False
        if self.function & 0x01:
            self.annunciate = True
        else:
            self.annunciate = False
        self.value = self.unpack()
        try:
            self.meta = p.auxdata[self.function>>4]
        except KeyError:
            self.meta = None

        self.updated = time.time()

    def getMessage(self):
        log.debug("Producing CAN message for {}. Value = {}".format(self.name, self.value))
        self.data = bytearray([])

        self.data.append(self.node % 256)
        if self.index:
            self.data.append(self.index % 256)
        else:
            self.data.append(0)

        self.data.append(self.function)
        self.data.extend(self.pack())
        self.__msg.data = self.data
        self.__msg.dlc = len(self.data)
        return self.__msg

    msg = property(getMessage, setMessage)

    def getFullName(self):
        if self.indexName:
            return "%s %s %i" % (self.__name, self.indexName, self.index + 1)
        else:
            return self.__name

    fullName = property(getFullName)

    def valueStr(self, units=False):
        if self.__identifier == 0x580: #Time
            return "%02i:%02i:%02i" % (self.value[0], self.value[1], self.value[2])
        elif self.__identifier == 0x581: #Date
            return "%i-%i-%i" % (self.value[0], self.value[1], self.value[2])
        else:
            if self.units:
                return str(self.value) + " " + self.units
            else:
                return str(self.value)

    def unpack(self):
        # TODO: Make sure that self.data is the right size.  Should log error
        #       and set the failure bit.
        if self.type == "UINT, USHORT[2]": #Unusual case of the date
            x = []
            x.append(getValue("UINT", self.data[0:2],1))
            x.append(getValue("USHORT", self.data[2:3], 1))
            x.append(getValue("USHORT", self.data[3:4], 1))
            for each in x:
                if each==None: self.__failure=True
        elif '[' in self.type:
            y = self.type.strip(']').split('[')
            if y[0] == 'CHAR':
                x = getValue(self.type, self.data, self.multiplier)
            else:
                x = []
                size = getTypeSize(y[0])
                for n in range(int(y[1])):
                    x.append(getValue(y[0], self.data[size*n:size*n+size], self.multiplier))
                for each in x:
                    if each==None: self.__failure=True
        else:
            x = getValue(self.type, self.data, self.multiplier)
            if x == None: self.__failure = True
        return x

    def pack(self):
        if self.type == "UINT, USHORT[2]": # unusual case of the date
           x=[]
           x.extend(setValue("UINT", self.value[0]))
           x.extend(setValue("USHORT", self.value[1]))
           x.extend(setValue("USHORT", self.value[2]))
           return x
        elif '[' in self.type:
            y = self.type.strip(']').split('[')
            #if y[0] == 'CHAR':
            #    return setValue(self.type, self.value)
            #else:
            x = []
            for n in range(int(y[1])):
                x.extend(setValue(y[0], self.value[n]))
            return x
        else:
            return setValue(self.type, self.value, self.multiplier)

    def __cmp__(self, other):
        if self.__identifier < other.__identifier:
            return -1
        elif self.__identifier > other.__identifier:
            return 1
        else:
            if self.index < other.index:
                return -1
            elif self.index > other.index:
                return 1
            else:
                return 0


    def __str__(self):
        s = '[' + str(self.node) + '] ' + self.name
        if self.meta: s = s + ' ' + self.meta
        if self.indexName:
            s = s + ' ' + self.indexName + ' ' + str(self.index+1)
        s = s + ': '
        if self.value != None:
            if isinstance(self.value, list):
                if self.type == "BYTE" or self.type == "WORD":
                    n = 0 #loop counter
                    for each in reversed(self.value):
                        if each == True:
                            s = s+'1'
                        else:
                            s = s+'0'
                        n += 1
                        if n % 4 == 0: #add a space every four bits
                            s = s+' '
                else:
                    for each in self.value:
                        s = s + str(each) + ','
                s = s.strip(', ')
            else:
               s = s + str(self.value)
            if self.units != None:
                s = s + ' ' + self.units
            if self.failure:
                s = s + ' [FAIL]'
            if self.quality:
                s = s + ' [QUAL]'
            if self.annunciate:
                s = s + ' [ANNUNC]'
        return s


class TwoWayMsg(object):
    """Represents 2 Way communication channel data"""
    def __init__(self, msg=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.type = "Request"

    def setMessage(self, msg):
        self.channel = int((msg.arbitration_id - 1760) /2)
        self.data = msg.data
        if msg.arbitration_id % 2 == 0:
            self.type = "Request"
        else:
            self.type = "Response"

    def getMessage(self):
        msg = can.Message(extended_id=False)
        msg.arbitration_id = self.channel*2 + 1760
        if self.type == "Response":
            msg.arbitration_id += 1
        msg.data = self.data
        return msg

    msg = property(getMessage, setMessage)

    def __str__(self):
        s = self.type + " on channel " + str(self.channel) + ': ' + str(self.data)
        return s


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
        self.sendNode = msg.arbitration_id -1792
        self.controlCode = msg.data[0]
        #self.destNode = msg.data[1]
        self.data = msg.data[1:]

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + 1792, extended_id=False)
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
        try:
            s = self.codes[self.controlCode]
        except IndexError:
            if self.controlCode < 128:
                s = "Reserved NSM "
            else:
                s = "User Defined NSM "
            s = s + str(self.controlCode)
        s += ' [' + str(self.sendNode) + ']'
        #s += "->[" + str(self.destNode) + '] '
        s += ":"
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
            if device: self.device = device
            if fwrev: self.fwrev = fwrev
            if model: self.model = model

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id -1792
        self.controlCode = msg.data[0]
        #TODO Raise error if controlCode is not 0x00
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
        msg = can.Message(arbitration_id=self.sendNode + 1792, extended_id=False)
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
        try:
            s = self.codes[self.controlCode]
        except IndexError:
            if self.controlCode < 128:
                s = "Reserved NSM "
            else:
                s = "User Defined NSM "
            s += str(self.controlCode)
        s += " [" + str(self.sendNode) + "]"
        s += "->[" + str(self.destNode) + "]"
        s += " device={}".format(self.device)
        s += " fwrev={}".format(self.fwrev)
        s += " model={}".format(self.model)
        return s


def getTypeSize(datatype):
    """Return the size of the CAN-FIX datatype in bytes"""
    table = {"BYTE":1, "WORD":2, "SHORT":1, "USHORT":1, "UINT":2,
             "INT":2, "DINT":4, "UDINT":4, "FLOAT":4, "CHAR":1}
    return table[datatype]


# This function takes the bytearray that is in data and converts it into a value.
# The table is a dictionary that contains the CAN-FIX datatype string as the
# key and a format string for the stuct.unpack function.
def getValue(datatype, data, multiplier):
    table = {"SHORT":"<b", "USHORT":"<B", "UINT":"<H",
             "INT":"<h", "DINT":"<l", "UDINT":"<L", "FLOAT":"<f"}
    x = None

    #This code handles the bit type data types
    if datatype == "BYTE":
        x = []
        for bit in range(8):
            if data[0] & (0x01 << bit):
                x.append(True)
            else:
                x.append(False)
        return x
    elif datatype == "WORD":
        x = []
        for bit in range(8):
            if data[0] & (0x01 << bit):
                x.append(True)
            else:
                x.append(False)
        for bit in range(8):
            if data[1] & (0x01 << bit):
                x.append(True)
            else:
                x.append(False)
        return x
    # If we get here then the data type is a numeric type or a CHAR
    try:
        x = struct.unpack(table[datatype], data)[0]
        return x * multiplier
    except KeyError:
        # If we get a KeyError on the dict then it's a CHAR
        if "CHAR" in datatype:
            return data.decode("utf-8")
        return None
    except struct.error:
        return None

def setValue(datatype, value, multiplier=1):
    table = {"SHORT":"<b", "USHORT":"<B", "UINT":"<H",
             "INT":"<h", "DINT":"<l", "UDINT":"<L", "FLOAT":"<f"}

    if datatype == "BYTE":
        return None
    elif datatype == "WORD":
        return None
    try:
        if datatype != "FLOAT":
            x = struct.pack(table[datatype], int(round(value / multiplier)))
        else:
            x = struct.pack(table[datatype], value / multiplier)
        return x
        #return [ord(y) for y in x] # Convert packed string into ints
    except KeyError:
        if "CHAR" in datatype:
            return [ord(value)]
        return None

def parseMessage(msg):
    """Determine what type of CAN-FIX msg this is and return an object
       that represents that msg type properly.  Returns None on error"""
    log.debug("Parsing message with ID = 0x{0:03X}".format(msg.arbitration_id))
    if msg.arbitration_id == 0: # Undefined
        return None
    elif msg.arbitration_id < 256:
        return NodeAlarm(msg)
    elif msg.arbitration_id < 1760:
        return Parameter(msg)
    elif msg.arbitration_id < 1792:
        return TwoWayMsg(msg)
    elif msg.arbitration_id < 2048:
        if msg.data[0] == 0x00:
            return NodeIdentification(msg)
        # Default we just return a generic NodeSpecific Message
        return NodeSpecific(msg)
    else:
        return None
