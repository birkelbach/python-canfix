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

class TestTwoWayMessage(unittest.TestCase):
    def setUp(self):
        pass

    def test_RequestMessageCh0(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(extended_id=False, arbitration_id=0x6E0, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x00)
        self.assertEqual(p.type,"Request")

    def test_RequestMessageCh1(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x01)
        self.assertEqual(p.type,"Request")

    def test_RequestMessageCh15(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(extended_id=False, arbitration_id=0x6FE, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x0F)
        self.assertEqual(p.type,"Request")

    def test_RequestMessageCh0NoData(self):
        msg = can.Message(extended_id=False, arbitration_id=0x6E0)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data,b'')
        self.assertEqual(p.channel, 0x00)
        self.assertEqual(p.type,"Request")

    def test_ResponseMessageCh0(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x00)
        self.assertEqual(p.type,"Response")

    def test_ResponseMessageCh1(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(extended_id=False, arbitration_id=0x6E3, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x01)
        self.assertEqual(p.type,"Response")

    def test_ResponseMessageCh15(self):
        d = bytearray([0x01, 0x00, 0xAB, 0xCD, 0xEF, 0xFF, 0xEE, 0x11])
        msg = can.Message(extended_id=False, arbitration_id=0x6FF, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.TwoWayMsg)
        self.assertEqual(p.data, b'\x01\x00\xAB\xCD\xEF\xFF\xEE\x11')
        self.assertEqual(p.channel, 0x0F)
        self.assertEqual(p.type,"Response")

    def test_ResponseMessageCh0NoData(self):
        msg = can.Message(extended_id=False, arbitration_id=0x6E1)
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
        self.assertEqual(m.arbitration_id, 0x6E0)
        self.assertEqual(m.data, bytearray([1, 2, 3, 4, 5, 6, 7, 8]))

    def test_CANMessageRequestCh1(self):
        p = canfix.TwoWayMsg()
        p.channel = 1
        p.data = bytearray([1, 2, 3, 4, 5, 6, 7, 8])
        p.type = "Request"
        m = p.msg
        self.assertEqual(m.arbitration_id, 0x6E2)
        self.assertEqual(m.data, bytearray([1, 2, 3, 4, 5, 6, 7, 8]))

    def test_CANMessageResponseCh0(self):
        p = canfix.TwoWayMsg()
        p.channel = 0
        p.data = bytearray([1, 2, 3, 4, 5, 6, 7, 8])
        p.type = "Response"
        m = p.msg
        self.assertEqual(m.arbitration_id, 0x6E1)
        self.assertEqual(m.data, bytearray([1, 2, 3, 4, 5, 6, 7, 8]))

    def test_CANMessageResponseCh1(self):
        p = canfix.TwoWayMsg()
        p.channel = 1
        p.data = bytearray([1, 2, 3, 4, 5, 6, 7, 8])
        p.type = "Response"
        m = p.msg
        self.assertEqual(m.arbitration_id, 0x6E3)
        self.assertEqual(m.data, bytearray([1, 2, 3, 4, 5, 6, 7, 8]))


if __name__ == '__main__':
    unittest.main()
