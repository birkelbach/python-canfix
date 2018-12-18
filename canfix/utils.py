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

def getTypeSize(datatype):
    """Return the size of the CAN-FIX datatype in bytes"""
    table = {"BYTE":1, "WORD":2, "SHORT":1, "USHORT":1, "UINT":2,
             "INT":2, "DINT":4, "UDINT":4, "FLOAT":4, "CHAR":1}
    return table[datatype]


# This function takes the bytearray that is in data and converts it into a value.
# The table is a dictionary that contains the CAN-FIX datatype string as the
# key and a format string for the stuct.unpack function.
def unpack(datatype, data, multiplier):
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

# This function takes a datatype, value and multiplier and converts the single
# value into a bytearray and returns that bytearray
def pack(datatype, value, multiplier):
    table = {"SHORT":"<b", "USHORT":"<B", "UINT":"<H",
             "INT":"<h", "DINT":"<l", "UDINT":"<L", "FLOAT":"<f"}

    if datatype == "BYTE":
        x = bytearray([0x00])
        for bit in range(8):
            if value[bit]:
                x[0] |= 0x01<<bit
    elif datatype == "WORD":
        x = bytearray([0x00, 0x00])
        for bit in range(8):
            if value[bit]:
                x[0] |= 0x01<<bit
            if value[bit+8]:
                x[1] |= 0x01<<bit
    else:
        try:
            if datatype != "FLOAT":
                x = struct.pack(table[datatype], int(round(value / multiplier)))
            else:
                x = struct.pack(table[datatype], value / multiplier)
        except KeyError:
            if "CHAR" in datatype:
                return [ord(value)]
            return None
    return x

# This function takes the data type, a byte array of data and
def getValue(datatype, data, multiplier = 1.0):
    # TODO: Make sure that self.data is the right size.  Should log error
    #       and set the failure bit.
    # TODO: Need to make these special cases more generic
    if datatype == "UINT,USHORT[2]": #Unusual case of the date
        x = []
        x.append(unpack("UINT", data[0:2], 1))
        x.append(unpack("USHORT", data[2:3], 1))
        x.append(unpack("USHORT", data[3:4], 1))
        # for each in x:
        #     if each==None: self.__failure=True
    elif datatype == "USHORT[3],UINT": #Unusual case of the time
        x = []
        x.append(unpack("USHORT", data[0:1], 1))
        x.append(unpack("USHORT", data[1:2], 1))
        x.append(unpack("USHORT", data[2:3], 1))
        x.append(unpack("UINT", data[3:7], 1))
        # for each in x:
        #     if each==None: self.__failure=True
    elif datatype == "INT[2],BYTE": #Unusual case of encoder
        x = []
        x.append(unpack("INT", data[0:2], 1))
        x.append(unpack("INT", data[2:4], 1))
        x.append(unpack("BYTE", data[4:5], 1))

    elif '[' in datatype:
        y = datatype.strip(']').split('[')
        if y[0] == 'CHAR':
            x = unpack(datatype, data, multiplier)
        else:
            x = []
            size = getTypeSize(y[0])
            for n in range(int(y[1])):
                x.append(unpack(y[0], data[size*n:size*n+size], multiplier))
            # for each in x:
            #     if each==None: self.__failure=True
    else:
        x = unpack(datatype, data, multiplier)
        #if x == None: self.__failure = True
    return x

def setValue(datatype, value, multiplier=1.0):
    if datatype == "UINT,USHORT[2]": # unusual case of the date
        x=bytearray([])
        x.extend(pack("UINT", value[0], 1))
        x.extend(pack("USHORT", value[1], 1))
        x.extend(pack("USHORT", value[2], 1))
        return x
    elif datatype == "USHORT[3],UINT": #Unusual case of the time
        x=bytearray([])
        x.extend(pack("USHORT", value[0], 1))
        x.extend(pack("USHORT", value[1], 1))
        x.extend(pack("USHORT", value[2], 1))
        x.extend(pack("UINT", value[3], 1))
        return x
    elif datatype == "INT[2],BYTE": #Unusual case of encoder
        x=bytearray([])
        x.extend(pack("INT", value[0], 1))
        x.extend(pack("INT", value[1], 1))
        x.extend(pack("BYTE", value[2], 1))
        return x
    elif '[' in datatype:
        y = datatype.strip(']').split('[')
        x = []
        for n in range(int(y[1])):
            x.extend(pack(y[0], value[n], 1))
        return x
    else:
        return pack(datatype, value, multiplier)
