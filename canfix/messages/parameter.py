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
            self.__msg = can.Message(arbitration_id=identifier, is_extended_id=False)
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
            self.__msg = can.Message(arbitration_id=x.id, is_extended_id=False)
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
        x = getValue(self.type, self.data, self.multiplier)
        # TODO: Make sure that self.data is the right size.  Should log error
        #       and set the failure bit.
        self.value = getValue(self.type, self.data, self.multiplier)
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
        self.data.extend(setValue(self.type, self.value, self.multiplier))
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
        try:
            if self.__identifier == 0x580: #Time
                return "%02i:%02i:%02i" % (self.value[0], self.value[1], self.value[2])
            elif self.__identifier == 0x581: #Date
                return "%i-%i-%i" % (self.value[0], self.value[1], self.value[2])
            elif self.__identifier in [0x11A, 0x11B, 0x300, 0x301, 0x302, 0x303, 0x304, 0x305, 0x306, 0x307]:
                s = f"{self.value[0]}, {self.value[1]}, "
                for bit in self.value[2]:
                    if bit:
                        s += '1'
                    else:
                        s += '0'
                return s
            elif self.type[:5] == 'BYTE[': # Handle byte arrays
                s = ''
                for b in self.value:
                    for bit in b:
                        if bit:
                            s += '1'
                        else:
                            s += '0'
                    s += ' '
                return s
            elif self.type =='BYTE' or self.type == 'WORD':
                s=''
                for i, bit in enumerate(self.value):
                    if bit:
                            s += '1'
                    else:
                        s += '0'
                    if i == 8:
                        s += ' '
                return s
            else:
                if self.units:
                    return "{:g} {}".format(self.value, self.units)
                else:
                    return str(self.value)
        except:
            return "ERR"


    def __eq__(self, other):
        return (self.__identifier*16 + self.index) == (other.__identifier*16 + other.index)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return (self.__identifier*16 + self.index) < (other.__identifier*16 + other.index)

    def __le__(self, other):
        return (self.__identifier*16 + self.index) <= (other.__identifier*16 + other.index)

    def __gt__(self, other):
        return (self.__identifier*16 + self.index) > (other.__identifier*16 + other.index)

    def __ge__(self, other):
        return (self.__identifier*16 + self.index) >= (other.__identifier*16 + other.index)


    def __str__(self):
        s = '[' + str(self.node) + '] ' + self.name
        if self.meta: s = s + ' ' + self.meta
        if self.indexName:
            s = s + ' ' + self.indexName + ' ' + str(self.index+1)
        s = s + ': '
        if self.value != None:
            s += self.valueStr(units=True)
        else:
            s = s + str(self.value)
        # if self.units != None:
        #     s = s + ' ' + self.units
        if self.failure:
            s = s + ' [FAIL]'
        if self.quality:
            s = s + ' [QUAL]'
        if self.annunciate:
            s = s + ' [ANNUNC]'
        return s
