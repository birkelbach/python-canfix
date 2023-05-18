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

class TestNodeAlarm(unittest.TestCase):
    def setUp(self):
        pass

    def test_FirstNodeNoDataFromMessage(self):
        d = bytearray([0x01, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x01, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.NodeAlarm)
        self.assertEqual(p.alarm, 1)
        self.assertEqual(p.data, b'\x00\x00\x00\x00\x00')
        self.assertEqual(p.node, 0x01)

    def test_LastNodeNoDataFromMessage(self):
        d = bytearray([0x01, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0xFF, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p,canfix.NodeAlarm)
        self.assertEqual(p.alarm, 1)
        self.assertEqual(p.data, b'\x00\x00\x00\x00\x00')
        self.assertEqual(p.node,255)

    def test_NodeMissingAlarmFromMessage(self):
        msg = can.Message(is_extended_id=False, arbitration_id=0x01)

        with self.assertRaises(ValueError):
            p = canfix.parseMessage(msg)

    def test_ZeroNodeNotNodeAlarm(self):
        d = bytearray([0x01, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x00, data=d)
        p = canfix.parseMessage(msg)
        self.assertNotIsInstance(p,canfix.NodeAlarm)

    def test_0x100NodeNotNodeAlarm(self):
        d = bytearray([0x01, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x100, data=d)
        p = canfix.parseMessage(msg)
        self.assertNotIsInstance(p,canfix.NodeAlarm)

    def test_CANMessageFromNodeAlarm(self):
        p = canfix.NodeAlarm()
        p.node = 0x01
        p.alarm = 7
        p.data = b'\x1A\x2B\x3C\x4D\x5E'
        m = p.msg
        self.assertEqual(m.data, b'\x07\x00\x1A\x2B\x3C\x4D\x5E')

        p = canfix.NodeAlarm()
        p.node = 0x01
        p.alarm = 43981
        #p.data = b'\x1A\x2B\x3C\x4D\x5E'
        m = p.msg
        self.assertEqual(m.data, b'\xCD\xAB')

    def test_CANMessageForgetToSetNode(self):
        p = canfix.NodeAlarm()
        p.alarm = 12
        with self.assertRaises(AttributeError):
            m = p.msg

    def test_CANMessageForgetToSetAlarm(self):
        p = canfix.NodeAlarm()
        p.node = 10
        with self.assertRaises(AttributeError):
            m = p.msg


if __name__ == '__main__':
    unittest.main()
