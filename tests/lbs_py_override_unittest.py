#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import copy

from decimal import Decimal

# make sure local overrides are loaded not the system-installed version
import gi.overrides
if not gi.overrides.__path__[0].endswith("src/python/gi/overrides"):
    local_overrides = None
    # our overrides don't take precedence, let's fix it
    for i, path in enumerate(gi.overrides.__path__):
        if path.endswith("src/python/gi/overrides"):
            local_overrides = path

    gi.overrides.__path__.remove(local_overrides)
    gi.overrides.__path__.insert(0, local_overrides)

from gi.repository.ByteSize import Size


class SizeTestCase(unittest.TestCase):

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

        actual = Size("100 B") / 10
        expected = Decimal("10")
        self.assertEqual(actual, expected)

        actual = Size("120 B") / 100
        expected = Decimal("1.2")
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

    def testDeepCopy(self):
        size1 = Size("1 GiB")
        size2 = copy.deepcopy(size1)

        self.assertIsNot(size1, size2)
        self.assertEqual(size1, size2)

#endclass

# script entry point
if __name__=='__main__':
    unittest.main()
#endif


