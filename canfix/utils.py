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

    dtypes = datatype.split(',')
    x = 0
    for dtype in dtypes:
        if '[' in dtype:
            y = dtype.strip(']').split('[')
            x += table[y[0]] * int(y[1])
        else:
            x += table[dtype]
    return x


# This function takes the bytearray that is in data and converts it into a value.
# The table is a dictionary that contains the CAN-FIX datatype string as the
# key and a format string for the stuct.unpack function.
def unpack(datatype, data, multiplier):
    table = {"SHORT":"<b", "USHORT":"<B", "UINT":"<H",
             "INT":"<h", "DINT":"<l", "UDINT":"<L", "FLOAT":"<f"}
    if len(data) == 0:
        return None
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
        if multiplier != 1:
            return x * multiplier
        else:
            return x
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
    table = {"BYTE":"<b", "WORD":"<H", "SHORT":"<b", "USHORT":"<B", "UINT":"<H",
             "INT":"<h", "DINT":"<l", "UDINT":"<L", "FLOAT":"<f"}

    # We represent the BYTE and WORD types as a list of bools but the caller
    # may just send us an int.  If it's the list we'll deal with it here
    # otherwise we'll deal with it as an int.
    if isinstance(value, list): 
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



def getValue(datatype, data, multiplier = 1.0):
    """Takes the data type, a byte array of data and the multiplier
       and converts that data to the proper types and returns the value."""
    dtypes = datatype.split(',')
    result = []
    i = 0  #This is to keep track of the index into data[]
    for dtype in dtypes:
        if '[' in dtype:
            y = dtype.strip(']').split('[')
            size = getTypeSize(y[0])
            count = int(y[1])
            if y[0] == 'CHAR':
                result.append(unpack('CHAR', data[i:i+(size*count)], multiplier))
            else:
                x = []
                for n in range(count):
                    x.append(unpack(y[0], data[(size*n+i):size*(n+i)+size], multiplier))
                result.extend(x)
            i += size * count
        else:
            size = getTypeSize(dtype)
            result.append(unpack(dtype, data[i:size*i+size], multiplier))
            i += size
    if len(result) == 1:
        return result[0]
    else:
        return result


def setValue(datatype, value, multiplier=1.0):
    """This function takes a datatype string a value and multiplier.  It converts
       the value to a bytearray based on the datatypes and returns that array."""
    dtypes = datatype.split(',')
    x = bytearray([])
    if len(dtypes) == 1:
        if '[' in datatype:
            y = datatype.strip(']').split('[')
            for n in range(int(y[1])):
                x.extend(pack(y[0], value[n], 1))
            return x
        else:
            return pack(datatype, value, multiplier)
    else:
        i = 0
        for dtype in dtypes:
            if '[' in dtype:
                y = dtype.strip(']').split('[')
                for n in range(int(y[1])):
                    x.extend(pack(y[0], value[i], 1))
                    i += 1
            else:
                x.extend(pack(dtype, value[i], multiplier))
                i += 1
        return x
