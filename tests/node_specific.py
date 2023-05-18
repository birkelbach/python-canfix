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
from canfix.globals import NODE_SPECIFIC_MSGS


class TestNodeSpecific(unittest.TestCase):
    def setUp(self):
        pass

    def test_NodeSpecificMessage(self):
        d = bytearray([0x61, 0x02, 0x03, 0x40, 0x50, 0x60, 0x70, 0x80])
        msg = can.Message(is_extended_id=False, arbitration_id=NODE_SPECIFIC_MSGS, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeSpecific)
        self.assertEqual(p.sendNode, 0x00)
        self.assertEqual(p.controlCode, 0x61)
        self.assertEqual(p.data, bytearray([0x02, 0x03, 0x40, 0x50, 0x60, 0x70, 0x80]))

        d = bytearray([0x61, 0x02, 0x03, 0x40, 0x50, 0x60, 0x70, 0x80])
        msg = can.Message(is_extended_id=False, arbitration_id=NODE_SPECIFIC_MSGS + 255, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeSpecific)
        self.assertEqual(p.sendNode, 0xFF)
        self.assertEqual(p.controlCode, 0x61)
        self.assertEqual(p.data, bytearray([0x02, 0x03, 0x40, 0x50, 0x60, 0x70, 0x80]))

    def test_NodeSpecificMessageNoData(self):
        d = bytearray([0x61])
        msg = can.Message(is_extended_id=False, arbitration_id=NODE_SPECIFIC_MSGS, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeSpecific)
        self.assertEqual(p.sendNode, 0x00)
        self.assertEqual(p.controlCode, 0x61)

    def test_NodeSpecificCANMessage(self):
        p = canfix.NodeSpecific()
        p.sendNode = 23
        p.controlCode = 0xFF
        m = p.msg
        self.assertEqual(m.arbitration_id, NODE_SPECIFIC_MSGS + 23)
        self.assertEqual(m.data, bytearray([0xFF]))

    def test_NodeSpecificCANMessageWithData(self):
        p = canfix.NodeSpecific()
        p.sendNode = 23
        p.controlCode = 0xFF
        p.data = bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07])
        m = p.msg
        self.assertEqual(m.arbitration_id, NODE_SPECIFIC_MSGS + 23)
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
        with self.assertRaises(TypeError):
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
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeIdentification)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x00)
        self.assertEqual(p.destNode, 0x02)
        self.assertEqual(p.msgType, canfix.MSG_REQUEST)

    def test_NodeIdentificationMessageResponse(self):
        d = bytearray([0x00, 0x02, 0x01, 0x40, 0x50, 0x60, 0x70, 0x80])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
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
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        with self.assertRaises(canfix.MsgSizeError):
            p = canfix.parseMessage(msg)
        d = bytearray([0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        with self.assertRaises(canfix.MsgSizeError):
            p = canfix.parseMessage(msg)


    def test_NodeIdentificationBuildResponse(self):
        n = canfix.NodeIdentification(device=12, fwrev=22, model=76543)
        n.sendNode = 0x01
        n.destNode = 0x02
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x01)
        self.assertEqual(n.msg.data, bytearray([0x00, 0x02, 0x01, 12, 22, 0xFF, 0x2A, 0x01]))
        self.assertEqual(n.msgType, canfix.MSG_RESPONSE)

    def test_NodeIdentificationBuildRequest(self):
        n = canfix.NodeIdentification()
        n.sendNode = 0x01
        n.destNode = 0x02
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x01)
        self.assertEqual(n.msg.data, bytearray([0x00, 0x02]))
        self.assertEqual(n.msgType, canfix.MSG_REQUEST)

    def test_NodeIdentificationBoundsChecks(self):
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


class TestBitRateSet(unittest.TestCase):
    def setUp(self):
        pass

    def test_BitRateSetMessageRequest(self):
        d = bytearray([0x01, 0x02, 0x01])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.BitRateSet)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x01)
        self.assertEqual(p.destNode, 0x02)
        self.assertEqual(p.msgType, canfix.MSG_REQUEST)
        self.assertEqual(p.bitrate, 1)

    def test_BitRateSetMessageResponse(self):
        d = bytearray([0x01, 0x02])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.BitRateSet)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x01)
        self.assertEqual(p.destNode, 0x02)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.status, canfix.MSG_SUCCESS)

        d = bytearray([0x01, 0x02, 0xFF])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.BitRateSet)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x01)
        self.assertEqual(p.destNode, 0x02)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.status, canfix.MSG_FAIL)

    def test_BitRateSetBuildRequest(self):
        n = canfix.BitRateSet(bitrate=1)
        n.sendNode = 0x01
        n.destNode = 0x02
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x01)
        self.assertEqual(n.msg.data, bytearray([0x01, 0x02, 0x01]))
        self.assertEqual(n.msgType, canfix.MSG_REQUEST)

    def test_BitRateSetBuildResponse(self):
        n = canfix.BitRateSet()
        n.sendNode = 0x01
        n.destNode = 0x02
        n.status = canfix.MSG_SUCCESS
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x01)
        self.assertEqual(n.msg.data, bytearray([0x01, 0x02]))
        self.assertEqual(n.msgType, canfix.MSG_RESPONSE)

        n.status = canfix.MSG_FAIL
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x01)
        self.assertEqual(n.msg.data, bytearray([0x01, 0x02, 0xFF]))
        self.assertEqual(n.msgType, canfix.MSG_RESPONSE)

    def test_BitRateSetBitRates(self):
        n = canfix.BitRateSet(bitrate=125)
        n.sendNode = 0x01
        n.destNode = 0x02
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x01)
        self.assertEqual(n.msg.data, bytearray([0x01, 0x02, 0x01]))
        self.assertEqual(n.msgType, canfix.MSG_REQUEST)
        n.bitrate = 250
        self.assertEqual(n.msg.data, bytearray([0x01, 0x02, 0x02]))
        n.bitrate = 500
        self.assertEqual(n.msg.data, bytearray([0x01, 0x02, 0x03]))
        n.bitrate = 1000
        self.assertEqual(n.msg.data, bytearray([0x01, 0x02, 0x04]))

    def test_BitRateSetBitRatesFail(self):
        with self.assertRaises(ValueError):
            n = canfix.BitRateSet(bitrate=0)
        with self.assertRaises(ValueError):
            n = canfix.BitRateSet(bitrate=5)
        with self.assertRaises(ValueError):
            n = canfix.BitRateSet(bitrate=12)
        with self.assertRaises(ValueError):
            n = canfix.BitRateSet(bitrate=1200)


class TestNodeIDSet(unittest.TestCase):
    def setUp(self):
        pass

    def test_NodeIDSetMessageRequest(self):
        d = bytearray([0x02, 0x03, 0x04])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeIDSet)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x02)
        self.assertEqual(p.destNode, 0x03)
        self.assertEqual(p.msgType, canfix.MSG_REQUEST)
        self.assertEqual(p.newNode, 4)

    def test_NodeIDeSetBuildRequest(self):
        n = canfix.NodeIDSet(newNode=3)
        n.sendNode = 0x05
        n.destNode = 0x01
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x05)
        self.assertEqual(n.msg.data, bytearray([0x02, 0x01, 0x03]))
        self.assertEqual(n.msgType, canfix.MSG_REQUEST)

    def test_NodeIDSetBuildResponse(self):
        n = canfix.NodeIDSet()
        n.sendNode = 0x03
        n.destNode = 0x01
        n.msgType = canfix.MSG_RESPONSE
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x02, 0x01, 0x00]))

    def test_NodeIDSetMsgSizeError(self):
        d = bytearray([0x02, 0x03, 0x04, 0x05])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        with self.assertRaises(canfix.MsgSizeError):
            p = canfix.parseMessage(msg)
        d = bytearray([0x02, 0x03])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        with self.assertRaises(canfix.MsgSizeError):
            p = canfix.parseMessage(msg)

    def test_NodeIDSetNodeIDError(self):
        n = canfix.NodeIDSet()
        n.sendNode = 0x05
        n.destNode = 0x01
        with self.assertRaises(ValueError):
            n.newNode = 0x00
        with self.assertRaises(ValueError):
            n.newNode = 256


class TestDisableParameter(unittest.TestCase):
    def setUp(self):
        pass

    def test_DisableParameterMessageRequest(self):
        d = bytearray([0x03, 0x04, 0x05, 0x01])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.DisableParameter)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x03)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.msgType, canfix.MSG_REQUEST)
        self.assertEqual(p.identifier, 261)

    def test_DisableParameterMessageResponse(self):
        d = bytearray([0x03, 0x04, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.DisableParameter)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x03)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.status, canfix.MSG_SUCCESS)

        d = bytearray([0x03, 0x04, 0x01])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.DisableParameter)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x03)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.status, canfix.MSG_FAIL)

    def test_DisableParameterBuildRequest(self):
        n = canfix.DisableParameter()
        n.sendNode = 0x03
        n.destNode = 0x01
        n.msgType = canfix.MSG_REQUEST
        n.identifier = 0x183
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x03, 0x01, 0x83, 0x01]))

    def test_DisableParameterBuildRequestString(self):
        n = canfix.DisableParameter()
        n.sendNode = 0x03
        n.destNode = 0x01
        n.msgType = canfix.MSG_REQUEST
        n.identifier = "Indicated Airspeed"
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x03, 0x01, 0x83, 0x01]))

    def test_DisableParameterBuildResponse(self):
        n = canfix.DisableParameter()
        n.sendNode = 0x03
        n.destNode = 0x01
        n.msgType = canfix.MSG_RESPONSE
        n.status = canfix.MSG_SUCCESS
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x03, 0x01, 0x00]))

        n.status = canfix.MSG_FAIL
        self.assertEqual(n.msg.data, bytearray([0x03, 0x01, 0x01]))

    def test_DisableParameterMsgSizeError(self):
        d = bytearray([0x03, 0x03, 0x04, 0x05, 0x06])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        with self.assertRaises(canfix.MsgSizeError):
            p = canfix.parseMessage(msg)
        d = bytearray([0x03, 0x03])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        with self.assertRaises(canfix.MsgSizeError):
            p = canfix.parseMessage(msg)

    def test_DisableParameterNodeIDError(self):
        n = canfix.DisableParameter()
        n.sendNode = 0x05
        n.destNode = 0x01
        n.identifier = 1759
        n.identifier = 256
        with self.assertRaises(ValueError):
            n.identifier = 1760
        with self.assertRaises(ValueError):
            n.identifier = 255
        with self.assertRaises(ValueError):
            n.identifier = "implied airspeed"


class TestEnableParameter(unittest.TestCase):
    def setUp(self):
        pass

    def test_EnableParameterMessageRequest(self):
        d = bytearray([0x04, 0x04, 0x05, 0x01])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.EnableParameter)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x04)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.msgType, canfix.MSG_REQUEST)
        self.assertEqual(p.identifier, 261)

    def test_EnableParameterMessageResponse(self):
        d = bytearray([0x04, 0x04, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.EnableParameter)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x04)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.status, canfix.MSG_SUCCESS)

        d = bytearray([0x04, 0x04, 0x01])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.EnableParameter)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x04)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.status, canfix.MSG_FAIL)

    def test_EnableParameterBuildRequest(self):
        n = canfix.EnableParameter()
        n.sendNode = 0x03
        n.destNode = 0x01
        n.msgType = canfix.MSG_REQUEST
        n.identifier = 0x183
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x04, 0x01, 0x83, 0x01]))

    def test_EnableParameterBuildRequestString(self):
        n = canfix.EnableParameter()
        n.sendNode = 0x03
        n.destNode = 0x01
        n.msgType = canfix.MSG_REQUEST
        n.identifier = "Indicated Airspeed"
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x04, 0x01, 0x83, 0x01]))

    def test_EnableParameterBuildResponse(self):
        n = canfix.EnableParameter()
        n.sendNode = 0x03
        n.destNode = 0x01
        n.msgType = canfix.MSG_RESPONSE
        n.status = canfix.MSG_SUCCESS
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x04, 0x01, 0x00]))

        n.status = canfix.MSG_FAIL
        self.assertEqual(n.msg.data, bytearray([0x04, 0x01, 0x01]))

    def test_EnableParameterMsgSizeError(self):
        d = bytearray([0x04, 0x03, 0x04, 0x05, 0x06])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        with self.assertRaises(canfix.MsgSizeError):
            p = canfix.parseMessage(msg)
        d = bytearray([0x04, 0x03])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        with self.assertRaises(canfix.MsgSizeError):
            p = canfix.parseMessage(msg)

    def test_EnableParameterNodeIDError(self):
        n = canfix.EnableParameter()
        n.sendNode = 0x05
        n.destNode = 0x01
        n.identifier = 1759
        n.identifier = 256
        with self.assertRaises(ValueError):
            n.identifier = 1760
        with self.assertRaises(ValueError):
            n.identifier = 255
        with self.assertRaises(ValueError):
            n.identifier = "implied airspeed"


class TestNodeReport(unittest.TestCase):
    def setUp(self):
        pass

    def test_NodeReportMessageRequest(self):
        d = bytearray([0x05, 0x04])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E1, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeReport)
        self.assertEqual(p.sendNode, 0x01)
        self.assertEqual(p.controlCode, 0x05)
        self.assertEqual(p.destNode, 0x04)

    def test_NodeReportBuildRequest(self):
        n = canfix.NodeReport()
        n.sendNode = 0x03
        n.destNode = 0x01
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x05, 0x01]))


class TestNodeStatus(unittest.TestCase):
    def setUp(self):
        pass

    def test_NodeStatusMessage(self):
        d = bytearray([0x06, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        p.type = "WORD"
        self.assertIsInstance(p, canfix.NodeStatus)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.controlCode, 0x06)
        self.assertEqual(p.parameter, 0x00)
        self.assertEqual(p.value, [False]*16)

    def test_NodeStatusBuild(self):
        n = canfix.NodeStatus()
        n.sendNode = 0x03
        n.parameter = 1 # Internal Temperature
        n.value = 65.3
        self.assertEqual(n.type, "INT")
        self.assertEqual(n.multiplier, 0.1)
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x06, 0x01, 0x00, 0x8D, 0x02]))

    def test_NodeStatusAllParametersBuild(self):
        wordval = [False]*16
        wordval[2] = True
        wordval[15] = True
        # Parameter, Value, Result
        tests = ((0x00, wordval, [0x04, 0x80]),
                 (0x01, 73.2, [0xDC, 0x02]),
                 (0x02, 14.2, [0x8E, 0x00]),
                 (0x03, 876543, [0xFF, 0x5F, 0x0D, 0x00]),
                 (0x04, 234567, [0x47, 0x94, 0x03, 0x00]),
                 (0x05, 123456789, [0x15, 0xCD, 0x5B, 0x07])
                )
        n = canfix.NodeStatus()
        n.sendNode = 0x04
        for each in tests:
            n.parameter = each[0]
            n.value = each[1]
            tr = bytearray([0x06, each[0], 0x00])
            tr.extend(each[2])
            self.assertEqual(n.msg.data, tr)


class TestUpdateFirmware(unittest.TestCase):
    def setUp(self):
        pass

    def test_UpdateFirmwareMessageRequest(self):
        d = bytearray([0x07, 0x04, 0x39, 0x30, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.UpdateFirmware)
        self.assertEqual(p.msgType, canfix.MSG_REQUEST)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.controlCode, 0x07)
        self.assertEqual(p.verification, 12345)
        self.assertEqual(p.channel, 0)

    def test_UpdateFirmwareMessageResponseFail(self):
        d = bytearray([0x07, 0x04, 0x01])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.UpdateFirmware)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.controlCode, 0x07)
        self.assertEqual(p.status, canfix.MSG_FAIL)
        self.assertEqual(p.errorCode, 0x01)

    def test_UpdateFirmwareMessageResponseSucceed(self):
        d = bytearray([0x07, 0x04, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.UpdateFirmware)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.controlCode, 0x07)
        self.assertEqual(p.status, canfix.MSG_SUCCESS)
        self.assertEqual(p.errorCode, 0x00)

    def test_UpdateFirmwareBuildRequest(self):
        n = canfix.UpdateFirmware()
        n.sendNode = 0x03
        n.destNode = 0x05
        n.verification = 54321
        n.channel = 0x02
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x07, 0x05, 0x31, 0xD4, 0x02]))

    def test_UpdateFirmwareBuildResponseFail(self):
        n = canfix.UpdateFirmware()
        n.sendNode = 0x03
        n.destNode = 0x05
        n.errorCode = 0x01
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x07, 0x05, 0x01]))

    def test_UpdateFirmwareBuildResponseSuccess(self):
        n = canfix.UpdateFirmware()
        n.sendNode = 0x03
        n.destNode = 0x05
        n.errorCode = 0x00
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x07, 0x05, 0x00]))


class TestTwoWayConnection(unittest.TestCase):
    def setUp(self):
        pass

    def test_TwoWayConnectionMessageRequest(self):
        d = bytearray([0x08, 0x04, 0x02, 0x39, 0x30])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.TwoWayConnection)
        self.assertEqual(p.msgType, canfix.MSG_REQUEST)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.controlCode, 0x08)
        self.assertEqual(p.connectionType, 12345)
        self.assertEqual(p.channel, 0x02)

    def test_TwoWayConnectionMessageResponseFail(self):
        d = bytearray([0x08, 0x04, 0x01])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.TwoWayConnection)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.controlCode, 0x08)
        self.assertEqual(p.status, canfix.MSG_FAIL)
        self.assertEqual(p.errorCode, 0x01)

    def test_TwoWayConnectionMessageResponseSucceed(self):
        d = bytearray([0x08, 0x04, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.TwoWayConnection)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.controlCode, 0x08)
        self.assertEqual(p.status, canfix.MSG_SUCCESS)
        self.assertEqual(p.errorCode, 0x00)

    def test_TwoWayConnectionBuildRequest(self):
        n = canfix.TwoWayConnection()
        n.sendNode = 0x03
        n.destNode = 0x05
        n.connectionType = 54321
        n.channel = 0x02
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x08, 0x05, 0x02, 0x31, 0xD4]))

    def test_TwoWayConnectionBuildResponseFail(self):
        n = canfix.TwoWayConnection()
        n.sendNode = 0x03
        n.destNode = 0x05
        n.errorCode = 0x01
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x08, 0x05, 0x01]))

    def test_TwoWayConnectionBuildResponseSuccess(self):
        n = canfix.TwoWayConnection()
        n.sendNode = 0x03
        n.destNode = 0x05
        n.errorCode = 0x00
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x08, 0x05, 0x00]))


class TestConfigurationSet(unittest.TestCase):
    def setUp(self):
        pass

    def test_ConfigurationSetMessageRequest(self):
        d = bytearray([0x09, 0x04, 0x0F, 0x00, 0x55])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        p.datatype = "BYTE"
        self.assertIsInstance(p, canfix.NodeConfigurationSet)
        self.assertEqual(p.msgType, canfix.MSG_REQUEST)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.key, 15)
        self.assertEqual(p.value, [True,False,True,False,True,False,True,False])

    def test_ConfigurationSetMessageResponseFail(self):
        d = bytearray([0x09, 0x05, 0x0F])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeConfigurationSet)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x05)
        self.assertEqual(p.status, canfix.MSG_FAIL)
        self.assertEqual(p.errorCode, 15)

    def test_ConfigurationSetMessageResponseSuccess(self):
        d = bytearray([0x09, 0x05, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeConfigurationSet)
        self.assertEqual(p.msgType, canfix.MSG_RESPONSE)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x05)
        self.assertEqual(p.status, canfix.MSG_SUCCESS)
        self.assertEqual(p.errorCode, 0)

    def test_NodeConfigurationSetResponseBuild(self):
        n = canfix.NodeConfigurationSet()
        n.sendNode = 0x03
        n.destNode = 0x05
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x09, 0x05, 0x00]))

    def test_NodeStatusBuild(self):
        n = canfix.NodeStatus()
        n.sendNode = 0x03
        n.parameter = 1 # Internal Temperature
        n.value = 65.3
        self.assertEqual(n.type, "INT")
        self.assertEqual(n.multiplier, 0.1)
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x06, 0x01, 0x00, 0x8D, 0x02]))

    def test_NodeConfigurationSetBuild(self):
        n = canfix.NodeConfigurationSet()
        n.sendNode = 0x03
        n.destNode = 0x05
        n.key = 1
        n.datatype = "INT"
        n.multiplier = 0.1
        n.value = 65.3
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x09, 0x05, 0x01, 0x00, 0x8D, 0x02]))


class TestConfigurationQuery(unittest.TestCase):
    def setUp(self):
        pass

    def test_ConfigurationQueryMessageRequest(self):
        d = bytearray([0x0A, 0x04, 0x0F, 0x00])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeConfigurationQuery)
        #self.assertEqual(p.msgType, canfix.MSG_REQUEST)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.key, 15)

    def test_ConfigurationQueryMessageResponseSuccess(self):
        d = bytearray([0x0A, 0x04, 0x00, 0x55])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        p.datatype = "BYTE"
        self.assertIsInstance(p, canfix.NodeConfigurationQuery)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.error, 0x00)
        self.assertEqual(p.value, [True,False,True,False,True,False,True,False])

    def test_ConfigurationQueryMessageResponseFail(self):
        d = bytearray([0x0A, 0x04, 0x01])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeConfigurationQuery)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.error, 0x01)

    def test_ConfigurationQueryBuildRequest(self):
        n = canfix.NodeConfigurationQuery()
        n.sendNode = 0x03
        n.destNode = 0x05
        n.key = 128
        #n.datatype = "FLOAT"
        #n.value = 65.3
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x0A, 0x05, 0x80, 0x00]))

    def test_ConfigurationQueryBuildResponse(self):
        n = canfix.NodeConfigurationQuery()
        n.sendNode = 0x03
        n.destNode = 0x05
        n.datatype = "FLOAT"
        n.value = 65.3
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.error, 0x00)
        self.assertEqual(n.msg.data, bytearray([0x0A, 0x05, 0x00, 0x9A, 0x99, 0x82, 0x42]))

    def test_ConfigurationQueryBuildResponseError(self):
        n = canfix.NodeConfigurationQuery()
        n.sendNode = 0x03
        n.destNode = 0x05
        n.datatype = "FLOAT"
        n.value = 65.3
        n.error = 0x01
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.error, 0x01)
        self.assertEqual(n.msg.data, bytearray([0x0A, 0x05, 0x01]))


class TestParameterSet(unittest.TestCase):
    def setUp(self):
        pass

    def test_ParameterSetMessage(self):
        d = bytearray([0x0C, 0x83, 0x19, 0x0F, 0x27])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.ParameterSet)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.index, 3)
        self.assertEqual(p.type, "UINT")
        self.assertEqual(p.multiplier, 0.1)
        self.assertTrue(abs(p.value - 999.9) < 0.1)

    def test_ParameterSetIndexCalc(self):
        for i in range(256):
            cc = (i // 32) + 0x0C
            x = (i % 32) << 11 | 0x183
            d = bytearray([cc, x % 256, x >> 8, 0x0F, 0x27])
            msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
            p = canfix.parseMessage(msg)
            self.assertIsInstance(p, canfix.ParameterSet)
            self.assertEqual(p.sendNode, 0x02)
            self.assertEqual(p.index, i)

    def test_ParameterSetBuild(self):
        n = canfix.ParameterSet(parameter="Indicated Airspeed")
        n.sendNode = 0x03
        n.value = 65.3
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x0C, 0x83, 0x01, 0x8D, 0x02]))

    def test_ParameterSetBuildIndexCalc(self):
        n = canfix.ParameterSet(parameter="Cylinder Head Temperature #1")
        n.sendNode = 0x34
        n.value = 204.3
        n.index = 35
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x34)
        self.assertEqual(n.msg.data, bytearray([0x0d, 0x00, 0x1D, 0xFB, 0x07]))


class TestNodeDescription(unittest.TestCase):
    def setUp(self):
        pass

    def test_NodeDescriptionMessage(self):
        d = bytearray([0x0B, 0x04, 0x01, 0x00, ord('A'), ord('B'), ord('C'), ord('D')])
        msg = can.Message(is_extended_id=False, arbitration_id=0x6E2, data=d)
        p = canfix.parseMessage(msg)
        self.assertIsInstance(p, canfix.NodeDescription)
        self.assertEqual(p.sendNode, 0x02)
        self.assertEqual(p.destNode, 0x04)
        self.assertEqual(p.packetnumber, 1)
        self.assertEqual(p.chars, bytearray([ord('A'), ord('B'), ord('C'), ord('D')]))

    def test_ParameterSetBuild(self):
        n = canfix.NodeDescription()
        n.sendNode = 0x03
        n.destNode = 0x04
        n.packetnumber = 0x13
        n.chars = "ABCD"
        self.assertEqual(n.msg.arbitration_id, NODE_SPECIFIC_MSGS+0x03)
        self.assertEqual(n.msg.data, bytearray([0x0B, 0x04, 0x13, 0x00, ord('A'), ord('B'), ord('C'), ord('D')]))

          

# TODO Test default destination node
# TODO Test __str__ outputs for requests and responses
# TODO Test error code strings
# TODO Test Node Description Message


if __name__ == '__main__':
    unittest.main()
