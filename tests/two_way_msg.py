#  Copyright (c) 2016 Phil Birkelbach
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

import unittest
import canfix
import can
from canfix.globals import TWOWAY_CONN_CHANS

class TestTwoWayMessage(unittest.TestCase):
    def setUp(self):
        pass

    def test_RequestMessageCh0(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(is_extended_id=False, arbitration_id=TWOWAY_CONN_CHANS, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x00)
        self.assertEqual(p.type,"Request")

    def test_RequestMessageCh1(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(is_extended_id=False, arbitration_id=TWOWAY_CONN_CHANS + 2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x01)
        self.assertEqual(p.type,"Request")

    def test_RequestMessageCh15(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(is_extended_id=False, arbitration_id=TWOWAY_CONN_CHANS + 14, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 7)
        self.assertEqual(p.type,"Request")

    def test_RequestMessageCh0NoData(self):
        msg = can.Message(is_extended_id=False, arbitration_id=TWOWAY_CONN_CHANS)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data,b'')
        self.assertEqual(p.channel, 0x00)
        self.assertEqual(p.type,"Request")

    def test_ResponseMessageCh0(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(is_extended_id=False, arbitration_id=0x7E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x00)
        self.assertEqual(p.type,"Response")

    def test_ResponseMessageCh1(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(is_extended_id=False, arbitration_id=0x7E3, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x01)
        self.assertEqual(p.type,"Response")

    def test_ResponseMessageCh15(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(is_extended_id=False, arbitration_id=0x7FF, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x0F)
        self.assertEqual(p.type,"Response")

    def test_ResponseMessageCh0NoData(self):
        msg = can.Message(is_extended_id=False, arbitration_id=TWOWAY_CONN_CHANS + 1)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data,b'')
        self.assertEqual(p.channel, 0x00)
        self.assertEqual(p.type,"Response")

    def test_CANMessageRequestCh0(self):
        p = canfix.TwoWayMsg()
        p.channel = 0
        p.data = bytearray([1, 2, 3, 4, 5, 6, 7, 8])
        p.type = "Request"
        m = p.msg
        self.assertEqual(m.arbitration_id, TWOWAY_CONN_CHANS)
        self.assertEqual(m.data, bytearray([1, 2, 3, 4, 5, 6, 7, 8]))

    def test_CANMessageRequestCh1(self):
        p = canfix.TwoWayMsg()
        p.channel = 1
        p.data = bytearray([1, 2, 3, 4, 5, 6, 7, 8])
        p.type = "Request"
        m = p.msg
        self.assertEqual(m.arbitration_id, TWOWAY_CONN_CHANS + 2)
        self.assertEqual(m.data, bytearray([1, 2, 3, 4, 5, 6, 7, 8]))

    def test_CANMessageResponseCh0(self):
        p = canfix.TwoWayMsg()
        p.channel = 0
        p.data = bytearray([1, 2, 3, 4, 5, 6, 7, 8])
        p.type = "Response"
        m = p.msg
        self.assertEqual(m.arbitration_id, TWOWAY_CONN_CHANS + 1)
        self.assertEqual(m.data, bytearray([1, 2, 3, 4, 5, 6, 7, 8]))

    def test_CANMessageResponseCh1(self):
        p = canfix.TwoWayMsg()
        p.channel = 1
        p.data = bytearray([1, 2, 3, 4, 5, 6, 7, 8])
        p.type = "Response"
        m = p.msg
        self.assertEqual(m.arbitration_id, TWOWAY_CONN_CHANS + 3)
        self.assertEqual(m.data, bytearray([1, 2, 3, 4, 5, 6, 7, 8]))


if __name__ == '__main__':
    unittest.main()
