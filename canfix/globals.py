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

import logging

log = logging.getLogger("canfix")

MSG_REQUEST =  0x01
MSG_RESPONSE = 0x02
MSG_SUCCESS =  0x00
MSG_FAIL =     0xFF

# From Table 2.1 of CANFIX spec
#
# High Priority Node Alarms 1 (0x1) - 255 (0xFF) 255
# High Priority Pilot Control Inputs 256 (0x100) - 319 (0x13F) 64
# High Priority Measured Positions 320 (0x140) - 383 (0x17F) 64
# High Priority Flight Data 384 (0x180) - 447 (0x1BF) 64
# High Priority Navigation Data 448 (0x1C0) - 511 (0x1FF) 64
# High Priority Engine / Aircraft System Data 512 (0x200) - 639 (0x27F) 128
# High Priority Auxiliary Data 640 (0x280) - 767 (0x2FF) 128
# Normal Priority Pilot Control Inputs 768 (0x300) - 895 (0x37F) 128
# Normal Priority Measured Positions 896 (0x380) - 1023 (0x3FF) 128
# Normal Priority Flight Data 1024 (0x400) - 1151 (0x47F) 128
# Normal Priority Navigation Data 1152 (0x480) - 1279 (0x4FF) 128
# Normal Priority Engine / Aircraft System Data 1280 (0x500) - 1407 (0x57F) 128
# Normal Priority Auxiliary Data 1408 (0x580) - 1535 (0x5FF) 128
# Future 1536 (0x600) - 1759 (0x6DF) 224
# Node Specific Messages 1760 (0x6E0) - 2015 (0x7DF) 256
NODE_SPECIFIC_MSGS = 0x6e0
# Two-Way Connection Channels 2016 (0x7E0) - 2047 (0x7FF) 32
TWOWAY_CONN_CHANS = 0x7e0

class MsgSizeError(Exception):
    pass

class TypeMissingError(Exception):
    pass

class NotFound(Exception):
    pass
