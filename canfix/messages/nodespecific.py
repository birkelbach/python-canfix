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


class NodeSpecific(object):
    """Represents a generic Node Specific Message"""
    codes = ["Node Identification", "Bit Rate Set", "Node ID Set", "Disable Parameter",
             "Enable Parameter", "Node Report", "Node Status", "Update Firmware",
             "Connection Request", "Node Configuration Set", "Node Configuration Query",
             "Node Description", "Parameter Set 0", "Parameter Set 32", "Parameter Set 64",
             "Parameter Set 96", "Parameter Set 128", "Parameter Set 160", "Parameter Set 192",
             "Parameter Set 224"]
    start_id = NODE_SPECIFIC_MSGS

    def __init__(self, msg=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.controlCode = None
            self.data = bytearray([])

    def setMessage(self, msg):
        log.debug(str(msg))
        self.sendNode = msg.arbitration_id - self.start_id
        self.controlCode = msg.data[0]
        #self.destNode = msg.data[1]
        self.data = msg.data[1:]

    def getMessage(self):
        msg = can.Message(arbitration_id=self.sendNode + self.start_id, is_extended_id=False)
        msg.data.append(self.controlCode)
        #msg.data.append(self.destNode)
        for each in self.data:
            msg.data.append(each)
        msg.dlc = len(msg.data)
        return msg

    msg = property(getMessage, setMessage)

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
