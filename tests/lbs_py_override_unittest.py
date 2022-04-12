#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest
import copy
import locale
import ctypes

from decimal import Decimal
from locale_utils import get_avail_locales, requires_locales

from bytesize import Size, ROUND_UP, ROUND_DOWN, KiB

class SizeTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        unittest.TestCase.setUpClass()
        cls.avail_locales = get_avail_locales()

    @requires_locales({'en_US.UTF-8'})
    def setUp(self):
        locale.setlocale(locale.LC_ALL,'en_US.UTF-8')
        self.addCleanup(self._clean_up)

    def _clean_up(self):
        locale.setlocale(locale.LC_ALL,'en_US.UTF-8')

    # test operator functions
    def testOperatorPlus(self):
        result = Size("1000 B") + Size("100 B")
        actual = result.get_bytes()
        expected = 1100
        self.assertEqual(actual, expected)

        result = Size("1000 B") + 10
        actual = result.get_bytes()
        expected = 1010
        self.assertEqual(actual, expected)

        result =  10 + Size("1000 B")
        actual = result.get_bytes()
        expected = 1010
        self.assertEqual(actual, expected)

        size1 = Size("100 B")
        size1 += Size("100 B")
        actual = size1.get_bytes()
        expected = 200
        self.assertEqual(actual, expected)

        size1 = Size("100 B")
        size1 += 100
        actual = size1.get_bytes()
        expected = 200
        self.assertEqual(actual, expected)

        # TODO shouldn't be the result int?
        int1 = 10
        int1 += Size("100 B")
        actual = int1.get_bytes()
        expected = 110
        self.assertEqual(actual, expected)

        size1 = Size("100 B") + None
        self.assertEqual(size1.get_bytes(), 100)
    #enddef

    def testOperatorMinus(self):
        result = Size("1000 B") - Size("100 B")
        actual = result.get_bytes()
        expected = 900
        self.assertEqual(actual, expected)

        result = Size("1000 B") - 10
        actual = result.get_bytes()
        expected = 990
        self.assertEqual(actual, expected)

        result = 10 - Size("100 B")
        actual = result.get_bytes()
        expected = -90
        self.assertEqual(actual, expected)

        size1 = Size("100 B")
        size1 -= Size("10 B")
        actual = size1.get_bytes()
        expected = 90
        self.assertEqual(actual, expected)

        size1 = Size("100 B")
        size1 -= 10
        actual = size1.get_bytes()
        expected = 90
        self.assertEqual(actual, expected)

        # TODO shouldn't be the result int?
        int1 = 1000
        int1 -= Size("100 B")
        actual = int1.get_bytes()
        expected = 900
        self.assertEqual(actual, expected)

        size1 = Size("100 B") - None
        self.assertEqual(size1.get_bytes(), 100)
    #enddef

    def testOperatorMul(self):
        result = Size("4 B") * 3
        actual = result.get_bytes()
        expected = 12
        self.assertEqual(actual, expected)

        result = 3 * Size("4 B")
        actual = result.get_bytes()
        expected = 12
        self.assertEqual(actual, expected)

        size1 = Size("4 B")
        size1 *= 3
        actual = size1.get_bytes()
        expected = 12
        self.assertEqual(actual, expected)

        int1 = 4
        int1 *= Size("3 B")
        actual = int1.get_bytes()
        expected = 12
        self.assertEqual(actual, expected)
    #enddef

    def testOperatorDiv(self):
        actual = Size("100 B") / Size("10 B")
        expected = Decimal("10")
        self.assertEqual(actual, expected)

        actual = Size("120 B") / Size("100 B")
        expected = Decimal("1.2")
        self.assertEqual(actual, expected)

        actual = Size("120 B") // Size("100 B")
        expected = Decimal("1")
        self.assertEqual(actual, expected)

        actual = Size("128 EiB") // Size("64 EiB")
        expected = 2
        self.assertEqual(actual, expected)

        actual = Size("100 B") / 10
        expected = Decimal("10")
        self.assertEqual(actual, expected)

        actual = Size("120 B") / 100
        expected = Decimal("1.2")
        self.assertEqual(actual, expected)

        actual = Size("128 EiB") // 2
        expected = Size("64 EiB")
        self.assertEqual(actual, expected)

        result = Size("120 B") // 100
        actual = result.get_bytes()
        expected = 1
        self.assertEqual(actual, expected)

        size1 = Size("120 B")
        size1 /= Size("100 B")
        actual = size1
        expected = Decimal("1.2")
        self.assertEqual(actual, expected)

        size1 = Size("120 B")
        size1 /= 100
        actual = size1
        expected = Decimal("1.2")
        self.assertEqual(actual, expected)

        size1 = Size("120 B")
        size1 //= Size("100 B")
        actual = size1
        expected = Decimal("1")
        self.assertEqual(actual, expected)
    #enddef

    def testDivMod(self):
        size1 = Size("120 B")
        q, mod = divmod(size1, Size("100 B"))

        self.assertEqual(q, 1)
        self.assertEqual(mod, Size("20 B"))

        size1 = Size("250 MiB")
        q, mod = divmod(size1, Size("100 MiB"))

        self.assertEqual(q, 2)
        self.assertEqual(mod, Size("50 MiB"))

        size1 = Size("10 GiB") + Size("5 GiB")
        q, mod = divmod(size1, 7)
        self.assertEqual(q, 2300875337)
        self.assertEqual(mod, 1)

    def testEquality(self):
        size1 = Size("1 GiB")
        size2 = Size("2 GiB")

        self.assertTrue(size1 == size1)
        self.assertTrue(size2 == size2)
        self.assertFalse(size1 == size2)
        self.assertFalse(size2 == size1)

        self.assertFalse(size1 == None)
        self.assertFalse(size1 == 0)

        size3 = Size(0)
        self.assertTrue(size3 == 0)
    #enddef

    def testCompare(self):
        size1 = Size("1 GiB")
        size2 = Size("2 GiB")

        self.assertTrue(size2 > size1)
        self.assertFalse(size1 > size2)
        self.assertTrue(size2 >= size1)
        self.assertFalse(size1 >= size2)
        self.assertTrue(size1 >= size1)

        self.assertFalse(size2 < size1)
        self.assertTrue(size1 < size2)
        self.assertFalse(size2 <= size1)
        self.assertTrue(size1 <= size2)
        self.assertTrue(size1 <= size1)

        self.assertTrue(size1 > None)
        self.assertTrue(size1 >= None)
        self.assertFalse(size1 < None)
        self.assertFalse(size1 <= None)
        self.assertFalse(size1 == None)
        self.assertTrue(size1 != None)

        size3 = Size(0)
        self.assertTrue(size3 > None)
        self.assertFalse(size3 < None)
        self.assertTrue(size3 != None)
    #enddef

    def testBool(self):
        size1 = Size("1 GiB")
        size2 = Size(0)

        self.assertTrue(size1)
        self.assertFalse(size2)
    #enddef

    def testInt(self):
        # just to make sure Size can be correctly interpreted as int in python 3.10
        ctypes.c_int(Size("1 GiB"))

    def testAbs(self):
        size1 = Size("1 GiB")
        self.assertEqual(size1, abs(size1))

        size2 = Size("-2 GiB")
        self.assertEqual(size2, -1 * abs(size2))

    def testNeg(self):
        size1 = Size("1 KiB")
        self.assertEqual(-1024, -size1)

        size1 = Size("-1 KiB")
        self.assertEqual(1024, -size1)

    def testDeepCopy(self):
        size1 = Size("1 GiB")
        size2 = copy.deepcopy(size1)

        self.assertIsNot(size1, size2)
        self.assertEqual(size1, size2)

    def testHashable(self):
        size = Size("1 KiB")
        hs = hash(size)
        self.assertIsNotNone(hs)

        size_set = set((Size("1 KiB"), Size("1 KiB"), Size("1 KiB"), Size("2 KiB"), Size(0)))
        self.assertEqual(len(size_set), 3)

    @requires_locales({'cs_CZ.UTF-8', 'ps_AF.UTF-8', 'en_US.UTF-8'})
    def testConvertTo(self):
        size = Size("1.5 KiB")
        conv = size.convert_to("KiB")
        self.assertEqual(conv, Decimal("1.5"))

        locale.setlocale(locale.LC_ALL,'cs_CZ.UTF-8')
        size = Size("1.5 KiB")
        conv = size.convert_to("KiB")
        self.assertEqual(conv, Decimal("1.5"))

        # this persian locale uses a two-byte unicode character for the radix
        locale.setlocale(locale.LC_ALL, 'ps_AF.UTF-8')
        size = Size("1.5 KiB")
        conv = size.convert_to("KiB")
        self.assertEqual(conv, Decimal("1.5"))

        locale.setlocale(locale.LC_ALL,'en_US.UTF-8')

    def testRoundToNearest(self):
        size = Size("1.5 KiB")
        conv = size.round_to_nearest(Size("1 KiB"), rounding=ROUND_UP)
        self.assertEqual(conv, Size("2 KiB"))

        conv = size.round_to_nearest(KiB, rounding=ROUND_DOWN)
        self.assertEqual(conv, Size("1 KiB"))

        with self.assertRaises(ValueError):
            size.round_to_nearest(-1, rounding=ROUND_UP)

#endclass

# script entry point
if __name__=='__main__':
    unittest.main()
#endif
