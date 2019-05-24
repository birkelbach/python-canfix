#  Copyright (c) 2018 Phil Birkelbach
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

from canfix.utils import setValue, getValue

class TestDataConversion(unittest.TestCase):
    def setUp(self):
        pass

    int_tests = [(2200,   bytearray([0x98, 0x08]), 1),
                 (-2200,  bytearray([0x68, 0xF7]), 1),
                 (0,      bytearray([0x00, 0x00]), 1),
                 (-1,     bytearray([0xFF, 0xFF]), 1),
                 (32767,  bytearray([0xFF, 0x7F]), 1),
                 (-32768, bytearray([0x00, 0x80]), 1)]

    def test_setvalue_basicint(self):
        for each in self.int_tests:
            x = setValue("INT",each[0], each[2])
            self.assertEqual(x, each[1])

    def test_getvalue_basicint(self):
        for each in self.int_tests:
            x = getValue("INT",each[1], each[2])
            self.assertEqual(x, each[0])

    uint_tests = [(2200,   bytearray([0x98, 0x08]), 1),
                  (0,      bytearray([0x00, 0x00]), 1),
                  (2000,   bytearray([0xD0, 0x07]), 1),
                  (32767,  bytearray([0xFF, 0x7F]), 1),
                  (65535 , bytearray([0xFF, 0xFF]), 1)]

    def test_setvalue_basicuint(self):
        for each in self.uint_tests:
            x = setValue("UINT",each[0], each[2])
            self.assertEqual(x, each[1])

    def test_getvalue_basicuint(self):
        for each in self.uint_tests:
            x = getValue("UINT",each[1], each[2])
            self.assertEqual(x, each[0])

    float_tests = [(3.1415920257568359375, bytearray([0xd8,0x0f,0x49,0x40])),
                   (0.0,                   bytearray([0x00,0x00,0x00,0x00])),
                   (89.99999237060546875,  bytearray([0xFF,0xFF,0xB3,0x42]))]

    def test_setvalue_basicfloat(self):
        for each in self.float_tests:
            x = setValue("FLOAT",each[0])
            self.assertEqual(x, each[1])

    def test_getvalue_basicfloat(self):
        for each in self.float_tests:
            x = getValue("FLOAT",each[1])
            self.assertEqual(x, each[0])

    def test_setvalue_basic_byte(self):
        y = [True, False, True]
        y.extend([False]*5)
        x = setValue("BYTE", y)
        self.assertEqual(x, bytearray([0x05]))

    def test_getvalue_basic_byte(self):
        y = [True, False, True]
        y.extend([False]*5)
        x = getValue("BYTE", bytearray([0x05]))
        self.assertEqual(x, y)

    def test_setvalue_basic_word(self):
        y = [True, False, True]
        y.extend([False]*5)
        y.extend(y)
        x = setValue("WORD", y)
        self.assertEqual(x, bytearray([0x05, 0x05]))

    def test_getvalue_basic_word(self):
        y = [True, False, True]
        y.extend([False]*5)
        y.extend(y)
        x = getValue("WORD", bytearray([0x05, 0x05]))
        self.assertEqual(x, y)

    def test_setvalue_compound(self):
        x = setValue("UINT,USHORT[2]", [21000, 121, 77]) # Date
        self.assertEqual(x, bytearray([0x08, 0x52, 0x79, 0x4D]))
        x = setValue("USHORT[3],UINT", [121, 77, 255, 21000]) # Time
        self.assertEqual(x, bytearray([ 0x79, 0x4D, 0xFF, 0x08, 0x52]))
        x = setValue("INT[2],BYTE", [5, -5, [True, False, True, False, False, False, False, False]]) # Encoder
        self.assertEqual(x, bytearray([ 0x05, 0x00, 0xFB, 0xFF, 0x05]))

    def test_getvalue_compound(self):
        x = getValue("UINT,USHORT[2]", bytearray([0x08, 0x52, 0x79, 0x4D])) # Date
        self.assertEqual(x, [21000, 121, 77])
        x = getValue("USHORT[3],UINT", bytearray([ 0x79, 0x4D, 0xFF, 0x08, 0x52])) # Time
        self.assertEqual(x, [121, 77, 255, 21000])
        x = getValue("INT[2],BYTE", bytearray([ 0x05, 0x00, 0xFB, 0xFF, 0x05])) # Encoder
        self.assertEqual(x, [5, -5, [True, False, True, False, False, False, False, False]])


# TODO: Add tests for...
#       multipliers
#       shorts
#       u shorts
#       chars
#       arrays
#       proper assertions when bad values are packed or unpacked

if __name__ == '__main__':
    unittest.main()
