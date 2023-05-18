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

class TestParameter(unittest.TestCase):
    def setUp(self):
        pass

    def test_None(self):
        d = bytearray([0x01, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x00, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p, None)

    def test_malformed(self):
        """
        The following should NOT assert
        """
        d = bytearray([0,0,4,0,0,0,0,0])
        msg = can.Message(is_extended_id=False, arbitration_id=0xc, data=d)
        p = canfix.parseMessage(msg)

        d = bytearray([1,2,3,4])
        msg = can.Message(is_extended_id=False, arbitration_id=0x123, data=d)
        p = canfix.parseMessage(msg)

        msg = can.Message(is_extended_id=False, arbitration_id=0x123, data=[0], is_error_frame=True)
        p = canfix.parseMessage(msg)
        self.assertTrue(p is None)

    def test_FirstNodeAlarm(self):
        d = bytearray([0x01, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x01, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeAlarm)
        self.assertEqual(p.node, 0x01)

    def test_LastNodeAlarm(self):
        d = bytearray([0x01, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0xFF, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeAlarm)
        self.assertEqual(p.node, 0xFF)

    def test_FirstParameter(self):
        d = bytearray([0x01, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x100, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.Parameter)
        self.assertEqual(p.node, 0x01)
        self.assertEqual(p.index, 2)
        self.assertEqual(p.function, 3)

    def test_LastDefinedParameter(self):
        d = bytearray([0x01, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x587, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.Parameter)
        self.assertEqual(p.node, 0x01)
        self.assertEqual(p.index, 2)
        self.assertEqual(p.function, 3)

    # TODO Right now undefined parameters raise an excpetion.
    # def test_LastParameter(self):
    #     d = bytearray([0x01, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
    #     msg = can.Message(is_extended_id=False, arbitration_id=0x6DF, data=d)
    #     p = canfix.parseMessage(msg)
    #     self.assertIsInstance(p, canfix.Parameter)
    #     self.assertEqual(p.node, 0x01)
    #     self.assertEqual(p.index, 2)
    #     self.assertEqual(p.function, 3)

    def test_FirstTwoWayMessage(self):
        d = bytearray([0x01, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x7E0, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.TwoWayMsg)
        self.assertEqual(p.channel, 0x00)
        self.assertEqual(p.type, "Request")

    def test_LastTwoWayMessage(self):
        d = bytearray([0x01, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x7FF, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.TwoWayMsg)
        self.assertEqual(p.channel, 0x0F)
        self.assertEqual(p.type, "Response")

    def test_FirstNodeSpecificMessage(self):
        d = bytearray([0x61, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E0, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeSpecific)
        self.assertEqual(p.sendNode, 0x00)
        self.assertEqual(p.controlCode, 0x61)

    def test_LastNodeSpecificMessage(self):
        d = bytearray([0x61, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x7DF, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeSpecific)
        self.assertEqual(p.sendNode, 0xFF)
        self.assertEqual(p.controlCode, 0x61)

if __name__ == '__main__':
    unittest.main()
