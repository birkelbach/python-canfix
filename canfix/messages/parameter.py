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

import sys
if sys.version_info[0] >= 3:
    unicode = str
import can
import time
from ..protocol import parameters, getParameterByName
from ..utils import getTypeSize, getValue, setValue
from ..globals import *


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
        x = getParameterByName(name)
        if x:
            log.debug("Setting parameter id to {}, based on name {}".format(x.id, name))
            self.__msg = can.Message(arbitration_id=x.id, extended_id=False)
            self.__identifier = x.id
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
        if isinstance(meta, str):
            try:
                meta = unicode(meta,"utf-8") # Can't really do this in Python3
            except:
                pass
        if isinstance(meta, int):
            self.function &= 0x0F
            self.function |= meta << 4
            self.__meta = parameters[self.__msg.arbitration_id].metadata[meta]
        elif isinstance(meta, unicode):
            p = parameters[self.__msg.arbitration_id]
            for each in p.metadata:
                if p.metadata[each].upper() == meta.upper():
                    self.function &= 0x0F
                    self.function |= each << 4
                    self.__meta = p.metadata[each] # Get's the case right
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
        x = self.function>>4
        self.meta = p.metadata[x] if x in p.metadata else None

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
        # TODO: Need to make these special cases more generic
        if self.type == "UINT,USHORT[2]": #Unusual case of the date
            x = []
            x.append(getValue("UINT", self.data[0:2], 1))
            x.append(getValue("USHORT", self.data[2:3], 1))
            x.append(getValue("USHORT", self.data[3:4], 1))
            for each in x:
                if each==None: self.__failure=True
        elif self.type == "USHORT[3],UINT": #Unusual case of the time
            x = []
            x.append(getValue("USHORT", self.data[0:1], 1))
            x.append(getValue("USHORT", self.data[1:2], 1))
            x.append(getValue("USHORT", self.data[2:3], 1))
            x.append(getValue("UINT", self.data[3:7], 1))
            for each in x:
                if each==None: self.__failure=True
        elif self.type == "INT[2],BYTE": #Unusual case of encoder
            x = []
            x.append(getValue("INT", self.data[0:2], 1))
            x.append(getValue("INT", self.data[2:4], 1))
            x.append(getValue("BYTE", self.data[4:5], 1))

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
        if self.type == "UINT,USHORT[2]": # unusual case of the date
            x=[]
            x.extend(setValue("UINT", self.value[0]))
            x.extend(setValue("USHORT", self.value[1]))
            x.extend(setValue("USHORT", self.value[2]))
            return x
        elif self.type == "USHORT[3],UINT": #Unusual case of the time
            x=[]
            x.extend(setValue("USHORT", self.value[0]))
            x.extend(setValue("USHORT", self.value[1]))
            x.extend(setValue("USHORT", self.value[2]))
            x.extend(setValue("UINT", self.value[3]))
            return x
        elif self.type == "INT[2],BYTE": #Unusual case of encoder
            x=[]
            x.extend(setValue("INT", self.value[0]))
            x.extend(setValue("INT", self.value[1]))
            x.extend(setValue("BYTE", self.value[2]))
        elif '[' in self.type:
            y = self.type.strip(']').split('[')
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