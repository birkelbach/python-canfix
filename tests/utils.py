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

from canfix.utils import getTypeSize

class TestGetTypeSize(unittest.TestCase):
    def setUp(self):
        pass

    def test_SimpleTypes(self):
        tests = {"BYTE":1, "WORD":2, "SHORT":1, "USHORT":1, "UINT":2,
                 "INT":2, "DINT":4, "UDINT":4, "FLOAT":4, "CHAR":1}

        for test in tests:
            self.assertEqual(getTypeSize(test), tests[test])

    def test_Arrays(self):
        self.assertEqual(getTypeSize("BYTE[2]"),2)
        self.assertEqual(getTypeSize("BYTE[3]"),3)
        self.assertEqual(getTypeSize("BYTE[5]"),5)
        self.assertEqual(getTypeSize("WORD[2]"),4)
        self.assertEqual(getTypeSize("SHORT[2]"),2)
        self.assertEqual(getTypeSize("SHORT[5]"),5)
        self.assertEqual(getTypeSize("USHORT[2]"),2)
        self.assertEqual(getTypeSize("USHORT[5]"),5)
        self.assertEqual(getTypeSize("UINT[2]"),4)
        self.assertEqual(getTypeSize("INT[2]"),4)
        self.assertEqual(getTypeSize("CHAR[2]"),2)
        self.assertEqual(getTypeSize("CHAR[3]"),3)
        self.assertEqual(getTypeSize("CHAR[5]"),5)

    def test_Compound(self):
        self.assertEqual(getTypeSize("BYTE,WORD"),3)
        self.assertEqual(getTypeSize("BYTE[2],WORD"),4)
        self.assertEqual(getTypeSize("BYTE,SHORT,USHORT"),3)
        self.assertEqual(getTypeSize("INT[2],BYTE"),5)
        # self.assertEqual(getTypeSize(""),)
        


if __name__ == '__main__':
    unittest.main()
