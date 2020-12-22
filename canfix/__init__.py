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

from .globals import *
from .messages import *

def parseMessage(msg, silent=False):
    """Determines the type of CAN-FIX msg

    This function takes a CAN message and determines what type of CAN-FIX
    message it is and returns an object that represents that particular
    type of CAN-FIX message.

    :param msg: The CAN message to parse
    :type msg: can.Message
    :param silent: If set to true return None instead of raising excpetions
    :type silent: bool, optional
    :returns:  A CAN-FIX message object

    """
    log.debug("Parsing message with ID = 0x{0:03X}".format(msg.arbitration_id))
    try:
        if msg.is_error_frame:
            return None
        if msg.arbitration_id == 0: # Undefined
            return None
        elif msg.arbitration_id < 256:
            return NodeAlarm(msg)
        elif msg.arbitration_id < 1536:
            return Parameter(msg)
        elif msg.arbitration_id < 2016:
            if msg.data[0] == 0x00:
                return NodeIdentification(msg)
            elif msg.data[0] == 0x01:
                return BitRateSet(msg)
            elif msg.data[0] == 0x02:
                return NodeIDSet(msg)
            elif msg.data[0] == 0x03:
                return DisableParameter(msg)
            elif msg.data[0] == 0x04:
                return EnableParameter(msg)
            elif msg.data[0] == 0x05:
                return NodeReport(msg)
            elif msg.data[0] == 0x06:
                return NodeStatus(msg)
            elif msg.data[0] == 0x07:
                return UpdateFirmware(msg)
            elif msg.data[0] == 0x08:
                return TwoWayConnection(msg)
            elif msg.data[0] == 0x09:
                return NodeConfigurationSet(msg)
            elif msg.data[0] == 0x0A:
                return NodeConfigurationQuery(msg)
            elif msg.data[0] == 0x0B:
                return NodeDescription(msg)
            elif msg.data[0] >= 0x0C and msg.data[0] <= 0x13:
                return ParameterSet(msg)
            else:
                return NodeSpecific(msg) #TODO This should probably be an error
        elif msg.arbitration_id < 2048:
            return TwoWayMsg(msg)

            # Default we just return a generic NodeSpecific Message
            return NodeSpecific(msg)
        else:
            return None
    except Exception as e:
        if silent:
            return None
        else:
            raise(e)
