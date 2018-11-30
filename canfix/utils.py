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
    except KeyError:
        if "CHAR" in datatype:
            return [ord(value)]
        return None
