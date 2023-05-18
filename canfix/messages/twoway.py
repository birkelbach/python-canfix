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
from ..globals import TWOWAY_CONN_CHANS

class TwoWayMsg(object):
    """Represents 2 Way communication channel data"""
    def __init__(self, msg=None):
        if msg != None:
            self.setMessage(msg)
        else:
            self.type = "Request"

    def setMessage(self, msg):
        self.channel = int((msg.arbitration_id - TWOWAY_CONN_CHANS) /2)
        self.data = msg.data
        if msg.arbitration_id % 2 == 0:
            self.type = "Request"
        else:
            self.type = "Response"

    def getMessage(self):
        msg = can.Message(is_extended_id=False)
        msg.arbitration_id = self.channel*2 + TWOWAY_CONN_CHANS
        if self.type == "Response":
            msg.arbitration_id += 1
        msg.data = self.data
        return msg

    msg = property(getMessage, setMessage)

    def __str__(self):
        s = self.type + " on channel " + str(self.channel) + ': ' + str(self.data)
        return s
