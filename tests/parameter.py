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

class TestParameterSimpleReceiver(unittest.TestCase):
    """In these tests we just try to spot check some parameters that represent
       different data types"""
    def setUp(self):
        pass

    def test_ParameterFlaps(self):
        d = bytearray([0x00, 0x00, 0x00, 0x01])
        msg = can.Message(arbitration_id=0x100, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Flap Control Switches #1")

    def test_ParameterEncoder(self):
        d = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(arbitration_id=0x11B, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Encoder Input (High Priority) #2")
        self.assertEqual(p.value, [0, 0, [False]*8])

        d = bytearray([0x00, 0x00, 0x00, 0xFB, 0xFF, 0x00, 0x00, 0x00])
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertEqual(p.value, [-5, 0, [False]*8])

        d = bytearray([0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00])
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertEqual(p.value, [5, 0, [False]*8])

    def test_ParameterPitchControlPosition(self):
        d = bytearray([0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(arbitration_id=0x124, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Pitch Control Position")
        self.assertEqual(p.value, 0)

        d = bytearray([0x00, 0x00, 0x00, 0xF0, 0xD8]) # -10,000
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertEqual(p.value, -100)

        d = bytearray([0x00, 0x00, 0x00, 0x10, 0x27]) # 10,000
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertEqual(p.value, 100)

        d = bytearray([0x00, 0x00, 0x00, 0x04, 0xd9]) # -9,980
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertEqual(p.value, -99.8)

    def test_ParameterIndicatedAirspeed(self):
        d = bytearray([0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(arbitration_id=0x183, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Indicated Airspeed")
        self.assertEqual(p.value, 0.0)

        d = bytearray([0x00, 0x00, 0x00, 0x0F, 0x27]) # 9999
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertLess(abs(p.value - 999.9), 0.005)

        d = bytearray([0x00, 0x00, 0x00, 0x87, 0x13]) # 4999
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertLess(abs(p.value - 499.9), 0.005)

    def test_ParameterIndicatedAltitude(self):
        d = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(arbitration_id=0x184, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Indicated Altitude")
        self.assertEqual(p.value, 0.0)

        d = bytearray([0x00, 0x00, 0x00, 0x18, 0xFC, 0xFF, 0xFF]) # -1,000
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertEqual(p.value, -1000)

        d = bytearray([0x00, 0x00, 0x00, 0x60, 0xEA, 0x00, 0x00]) # 60,000
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertEqual(p.value, 60000)

    def test_ParameterLatitude(self):

        d = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(arbitration_id=0x1C3, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Aircraft Position Latitude")
        self.assertEqual(p.value, 0.0)
        d = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0xB4, 0x42]) # 90.0
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertLess(abs(p.value - 90.0), 0.00005)

        d = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0xB4, 0xc2]) # 4999
        msg.data = d
        p = canfix.parseMessage(msg)
        self.assertLess(abs(p.value - -90.0), 0.00005)

    def test_ParameterAircraftIdentifier(self):
        d = bytearray([0x00, 0x00, 0x00, 0x37, 0x32, 0x37, 0x57, 0x42])
        msg = can.Message(arbitration_id=0x587, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Aircraft Identifier")
        self.assertEqual(p.value, "727WB")

    def test_ParameterTime(self):
        d = bytearray([0x02, 0x00, 0x00, 13, 23, 59, 0x2C, 0x02])
        msg = can.Message(arbitration_id=0x580, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Time")
        self.assertEqual(p.value, [13, 23, 59, 556])

    def test_ParameterDate(self):
        d = bytearray([0x02, 0x00, 0x00, 0xE0, 0x07, 7, 27])
        msg = can.Message(arbitration_id=0x581, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Date")
        self.assertEqual(p.value, [2016, 7, 27])


    # TODO Right now parameters that don't have enough bytes will return None
    # for the value.  Is this really what we want?  Might should raise an
    # exception.
    def test_ParameterShortData(self):
        d = bytearray([0x00, 0x00, 0x00, 0x00, 0x00])
        msg = can.Message(arbitration_id=0x184, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Indicated Altitude")
        self.assertEqual(p.value, None)


    def test_ParameterIndex(self):
        d = bytearray([0x00, 0x00, 0x00, 0xd2, 0x04])
        msg = can.Message(arbitration_id=0x501, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Cylinder Head Temperature #2")
        self.assertEqual(p.value, 123.4)
        self.assertEqual(p.index, 0)

        d = bytearray([0x00, 0x01, 0x00, 0xd2, 0x04])
        msg = can.Message(arbitration_id=0x501, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Cylinder Head Temperature #2")
        self.assertEqual(p.value, 123.4)
        self.assertEqual(p.index, 1)

        d = bytearray([0x00, 0xFF, 0x00, 0xd2, 0x04])
        msg = can.Message(arbitration_id=0x501, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Cylinder Head Temperature #2")
        self.assertEqual(p.value, 123.4)
        self.assertEqual(p.index, 255)

    def test_ParameterQuality(self):
        d = bytearray([0x00, 0x00, 0x00, 0xd2, 0x04])
        msg = can.Message(arbitration_id=0x501, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Cylinder Head Temperature #2")
        self.assertEqual(p.value, 123.4)
        self.assertEqual(p.annunciate, False)
        self.assertEqual(p.quality, False)
        self.assertEqual(p.failure, False)

        d = bytearray([0x00, 0x00, 0x01, 0xd2, 0x04])
        msg = can.Message(arbitration_id=0x501, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Cylinder Head Temperature #2")
        self.assertEqual(p.value, 123.4)
        self.assertEqual(p.annunciate, True)
        self.assertEqual(p.quality, False)
        self.assertEqual(p.failure, False)

        d = bytearray([0x00, 0x00, 0x02, 0xd2, 0x04])
        msg = can.Message(arbitration_id=0x501, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Cylinder Head Temperature #2")
        self.assertEqual(p.value, 123.4)
        self.assertEqual(p.annunciate, False)
        self.assertEqual(p.quality, True)
        self.assertEqual(p.failure, False)

        d = bytearray([0x00, 0x00, 0x04, 0xd2, 0x04])
        msg = can.Message(arbitration_id=0x501, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Cylinder Head Temperature #2")
        self.assertEqual(p.value, 123.4)
        self.assertEqual(p.annunciate, False)
        self.assertEqual(p.quality, False)
        self.assertEqual(p.failure, True)

        d = bytearray([0x00, 0x00, 0x07, 0xd2, 0x04])
        msg = can.Message(arbitration_id=0x501, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Cylinder Head Temperature #2")
        self.assertEqual(p.value, 123.4)
        self.assertEqual(p.annunciate, True)
        self.assertEqual(p.quality, True)
        self.assertEqual(p.failure, True)

    def test_ParameterMeta(self):
        d = bytearray([0x00, 0x00, 0x00, 0x1c, 0x04]) # 1052
        msg = can.Message(arbitration_id=0x183, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Indicated Airspeed")
        self.assertEqual(p.value, 105.2)
        self.assertEqual(p.meta, None)

        d = bytearray([0x00, 0x00, 0x10, 0x1c, 0x04]) # 1052
        msg = can.Message(arbitration_id=0x183, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Indicated Airspeed")
        self.assertEqual(p.value, 105.2)
        self.assertEqual(p.meta, 'Min')

        d = bytearray([0x00, 0x00, 0xF0, 0x1c, 0x04]) # 1052
        msg = can.Message(arbitration_id=0x183, is_extended_id=False, data=d)
        p = canfix.parseMessage(msg)
        self.assertEqual(p.name, "Indicated Airspeed")
        self.assertEqual(p.value, 105.2)
        self.assertEqual(p.meta, 'Vy')


class TestParameterSimpleSender(unittest.TestCase):
    """Here we are creating different parameters and making sure that they
       produce the correct CAN messages"""
    def setUp(self):
        pass

    def test_ParameterPitch(self):
        p = canfix.Parameter()
        p.node = 0x02
        p.name = "Pitch Angle"
        p.value = -1.02
        msg = p.msg

        self.assertEqual(msg.arbitration_id, 0x180)
        self.assertEqual(msg.data, bytearray([0x02, 0x00, 0x00, 0x9a, 0xff]))
        self.assertEqual(msg.dlc,5)

    def test_ParameterLongitude(self):
        p = canfix.Parameter()
        p.node = 0x02
        p.name = "Aircraft Position Longitude"
        p.value = -115.324
        msg = p.msg

        self.assertEqual(msg.arbitration_id, 0x1C4)
        self.assertEqual(msg.data, bytearray([0x02, 0x00, 0x00, 0xE3, 0xA5, 0xE6, 0xC2]))
        self.assertEqual(msg.dlc,7)

    def test_ParameterAircraftIdentifier(self):
        p = canfix.Parameter()
        p.node = 0x02
        p.name = "Aircraft Identifier"
        p.value = '727WB'
        msg = p.msg

        self.assertEqual(msg.arbitration_id, 0x587)
        self.assertEqual(msg.data, bytearray([0x02, 0x00, 0x00, 0x37, 0x32, 0x37, 0x57, 0x42]))
        self.assertEqual(msg.dlc,8)

    def test_ParameterTime(self):
        p = canfix.Parameter()
        p.node = 0x02
        p.name = "Time"
        p.value = [13, 14, 15, 556]
        msg = p.msg

        self.assertEqual(msg.arbitration_id, 0x580)
        self.assertEqual(msg.data, bytearray([0x02, 0x00, 0x00, 13, 14, 15, 0x2C, 0x02]))
        self.assertEqual(msg.dlc,8)

    def test_ParameterDate(self):
        p = canfix.Parameter()
        p.node = 0x02
        p.name = "Date"
        p.value = [1970, 7, 27]
        msg = p.msg

        self.assertEqual(msg.arbitration_id, 0x581)
        self.assertEqual(msg.data, bytearray([0x02, 0x00, 0x00, 0xB2, 0x07, 7, 27]))
        self.assertEqual(msg.dlc,7)

    def test_ParameterIDsToNames(self):
        p = canfix.Parameter()
        p.identifier = 0x183
        self.assertEqual(p.name, "Indicated Airspeed")
        p.identifier = 0x40B
        self.assertEqual(p.name, "Wind Direction")
        p.identifier = 0x38B
        self.assertEqual(p.name, "Fuel Pump Status #1")
        p.identifier = 0x281
        self.assertEqual(p.name, "Cabin Altitude")
        p.identifier = 0x103
        self.assertEqual(p.name, "Trim Switches #2")

    def test_ParameterMetaData(self):
        p = canfix.Parameter()
        p.identifier = 0x200
        p.node = 2
        p.meta = "Low Warn"
        p.value = 1700
        msg = p.msg
        self.assertEqual(msg.data, bytearray([0x02, 0x00, 0x40, 0xA4, 0x06]))
        self.assertEqual(msg.dlc,5)

        p.meta = "Min"
        msg = p.msg
        self.assertEqual(msg.data, bytearray([0x02, 0x00, 0x10, 0xA4, 0x06]))
        self.assertEqual(msg.dlc,5)

    def test_ParameterFlags(self):
        p = canfix.Parameter()
        p.node = 5
        p.identifier = 0x220
        p.value = 75.6
        p.annunciate = True
        p.quality = False
        p.failure = False
        msg = p.msg
        self.assertEqual(msg.data, bytearray([0x05, 0x00, 0x01, 0x88, 0x1D]))
        self.assertEqual(msg.dlc,5)

        p.annunciate = True
        p.quality = False
        p.failure = False
        msg = p.msg
        self.assertEqual(msg.data, bytearray([0x05, 0x00, 0x01, 0x88, 0x1D]))
        self.assertEqual(msg.dlc,5)

        p.annunciate = False
        p.quality = True
        p.failure = False
        msg = p.msg
        self.assertEqual(msg.data, bytearray([0x05, 0x00, 0x02, 0x88, 0x1D]))
        self.assertEqual(msg.dlc,5)

        p.annunciate = False
        p.quality = False
        p.failure = True
        msg = p.msg
        self.assertEqual(msg.data, bytearray([0x05, 0x00, 0x04, 0x88, 0x1D]))
        self.assertEqual(msg.dlc,5)

        p.annunciate = True
        p.quality = False
        p.failure = True
        msg = p.msg
        self.assertEqual(msg.data, bytearray([0x05, 0x00, 0x05, 0x88, 0x1D]))
        self.assertEqual(msg.dlc,5)


if __name__ == '__main__':
    unittest.main()
