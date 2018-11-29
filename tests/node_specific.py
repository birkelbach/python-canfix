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


class TestNodeSpecific(unittest.TestCase):
    def setUp(self):
        pass

    def test_NodeSpecificMessage(self):
        d = bytearray([0x01, 0x02, 0x03, 0x40, 0x50, 0x60, 0x70, 0x80])
        msg = can.Message(extended_id=False, arbitration_id=0x700, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeSpecific)
        self.assertEqual(p.sendNode, 0x00)
        self.assertEqual(p.controlCode, 0x01)
        self.assertEqual(p.data, bytearray([0x02, 0x03, 0x40, 0x50, 0x60, 0x70, 0x80]))

        d = bytearray([0x01, 0x02, 0x03, 0x40, 0x50, 0x60, 0x70, 0x80])
        msg = can.Message(extended_id=False, arbitration_id=0x7FF, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeSpecific)
        self.assertEqual(p.sendNode, 0xFF)
        self.assertEqual(p.controlCode, 0x01)
        self.assertEqual(p.data, bytearray([0x02, 0x03, 0x40, 0x50, 0x60, 0x70, 0x80]))

    def test_NodeSpecificMessageNoData(self):
        d = bytearray([0x05])
        msg = can.Message(extended_id=False, arbitration_id=0x700, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeSpecific)
        self.assertEqual(p.sendNode, 0x00)
        self.assertEqual(p.controlCode, 0x05)

    def test_NodeSpecificCANMessage(self):
        p = canfix.NodeSpecific()
        p.sendNode = 23
        p.controlCode = 0xFF
        m = p.msg
        self.assertEqual(m.arbitration_id, 0x700 + 23)
        self.assertEqual(m.data, bytearray([0xFF]))

    def test_NodeSpecificCANMessageWithData(self):
        p = canfix.NodeSpecific()
        p.sendNode = 23
        p.controlCode = 0xFF
        p.data = bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07])
        m = p.msg
        self.assertEqual(m.arbitration_id, 0x700 + 23)
        self.assertEqual(m.data, bytearray([0xFF, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]))

    # def test_NodeSpecificCANMessageNodeNotSet1(self):
    #     p = canfix.NodeSpecific()
    #     p.sendNode = 23
    #     p.controlCode = 0xFF
    #     with self.assertRaises(AttributeError):
    #         m = p.msg

    def test_NodeSpecificCANMessageNodeNotSet2(self):
        p = canfix.NodeSpecific()
        #p.sendNode = 23
        p.controlCode = 0xFF
        with self.assertRaises(AttributeError):
            m = p.msg

    # TODO is this the behaviour that we want?  Should it pass?
    def test_NodeSpecificCANMessageCCNotSet(self):
        p = canfix.NodeSpecific()
        p.sendNode = 23
        p.destNode = 1
        #p.controlCode = 0xFF
        m = p.msg

    # def test_NodeSpecific_setNodeIdentification(self):
    #     # Test the setNodeIdentification() Function
    #     p = canfix.NodeSpecific()
    #     p.sendNode = 21
    #     p.destNode = 22
    #     p.setNodeIdentification(0x23, 0x01, 0x010203)
    #     self.assertEqual(p.msg.data, bytearray([22,0x00,0x01,0x23,0x01,0x03,0x02,0x01]))
    #     with self.assertRaises(ValueError):
    #           p.setNodeIdentification(256, 0x01, 0x010203)
    #     with self.assertRaises(ValueError):
    #           p.setNodeIdentification(-1, 0x01, 0x010203)
    #     with self.assertRaises(ValueError):
    #           p.setNodeIdentification(1, 256, 0x010203)
    #     with self.assertRaises(ValueError):
    #           p.setNodeIdentification(1, -1, 0x010203)
    #     with self.assertRaises(ValueError):
    #           p.setNodeIdentification(1, 1, -1)
    #     with self.assertRaises(ValueError):
    #           p.setNodeIdentification(1, 1, 0x1000000)

class TestNodeIdentification(unittest.TestCase):
    def setUp(self):
        pass

    def test_NodeIdentificationMessageRequest(self):
        d = bytearray([0x00, 0x02])
        msg = can.Message(extended_id=False, arbitration_id=0x701, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeIdentification)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x00)
        self.assertEqual(p.destNode, 0x02)
        self.assertEqual(p.msgType, canfix.MSG_REQUEST)

    def test_NodeIdentificationMessageResponse(self):
        d = bytearray([0x00, 0x02, 0x01, 0x40, 0x50, 0x60, 0x70, 0x80])
        msg = can.Message(extended_id=False, arbitration_id=0x701, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeIdentification)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x00)
        self.assertEqual(p.destNode, 0x02)
        self.assertEqual(p.device, 0x40)
        self.assertEqual(p.fwrev, 0x50)
        self.assertEqual(p.model, 8417376)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)

    def test_NodeIdentificationMessageSizeError(self):
        d = bytearray([0x00, 0x02, 0x01, 0x40, 0x50, 0x60, 0x70])
        msg = can.Message(extended_id=False, arbitration_id=0x701, data=d)
        with self.assertRaises(canfix.MsgSizeError):
            p = canfix.parseMessage(msg)

    def testNodeIdentificationBuildRequest(self):
        n = canfix.NodeIdentification(device=12, fwrev=22, model=76543)
        n.sendNode = 0x01
        n.destNode = 0x02
        self.assertEqual(n.msg.arbitration_id, 0x700+0x01)
        self.assertEqual(n.msg.data, bytearray([0x00, 0x02, 0x01, 12, 22, 0xFF, 0x2A, 0x01]))
        self.assertEqual(n.msgType, canfix.MSG_RESPONSE)

    def testNodeIdentificationBuildResponse(self):
        n = canfix.NodeIdentification()
        n.sendNode = 0x01
        n.destNode = 0x02
        self.assertEqual(n.msg.arbitration_id, 0x700+0x01)
        self.assertEqual(n.msg.data, bytearray([0x00, 0x02]))
        self.assertEqual(n.msgType, canfix.MSG_REQUEST)

    def testNodeIdentificationBoundsChecks(self):
        with self.assertRaises(ValueError):
              n = canfix.NodeIdentification(device=256,fwrev= 0x01, model=0x010203)
        with self.assertRaises(ValueError):
              n = canfix.NodeIdentification(device=-1, fwrev=0x01, model=0x010203)
        with self.assertRaises(ValueError):
              n = canfix.NodeIdentification(device=1, fwrev=256, model=0x010203)
        with self.assertRaises(ValueError):
              n = canfix.NodeIdentification(device=1, fwrev=-1, model=0x010203)
        with self.assertRaises(ValueError):
              n = canfix.NodeIdentification(device=1, fwrev=1, model=-1)
        with self.assertRaises(ValueError):
              n = canfix.NodeIdentification(device=1, fwrev=1, model=0x1000000)


    # TODO Test default destination node
    # TODO Check STR outputs


if __name__ == '__main__':
    unittest.main()
