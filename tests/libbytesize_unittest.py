#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import locale
import unittest
from gi.repository.ByteSize import Size
from gi.repository import ByteSize

class SizeTestCase(unittest.TestCase):

    def testNew(self):
        actual = Size.new().get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef

    def setUp(self):
        locale.setlocale(locale.LC_ALL,'en_US.utf8')
    #enddef

    def tearDown(self):
        locale.setlocale(locale.LC_ALL,'en_US.utf8')
    #enddef

    def testNewFromStr(self):
        actual = Size.new_from_str('0 B').get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        actual = Size.new_from_str('1 KiB').get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)

        actual = Size.new_from_str('1KB').get_bytes()
        expected = (1000, 1)
        self.assertEqual(actual, expected)

        actual = Size.new_from_str('1 MiB').get_bytes()
        expected = (1048576, 1)
        self.assertEqual(actual, expected)

        actual = Size.new_from_str('-1.5 GiB').get_bytes()
        expected = (1610612736, -1)
        self.assertEqual(actual, expected)

        # TODO known bug, uncomment
        #locale.setlocale(locale.LC_ALL,'czech')

        #actual = Size.new_from_str('-1,5 KB').get_bytes()
        #expected = (1610612736, -1)
        #self.assertEqual(actual, expected)

        #locale.setlocale(locale.LC_ALL,'en_US.utf8')

    #enddef

    def testNewFromBytes(self):
        actual = Size.new_from_bytes(0, 0).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        actual = Size.new_from_bytes(10, 1).get_bytes()
        expected = (10, 1)
        self.assertEqual(actual, expected)

        actual = Size.new_from_bytes(1024, -1).get_bytes()
        expected = (1024, -1)
        self.assertEqual(actual, expected)
    #enddef

    def testNewFromSize(self):
        tempSize = Size.new_from_bytes(17, 1)
        actual = Size.new_from_size(tempSize).get_bytes()
        expected = (17, 1)
        self.assertEqual(actual, expected)
    #enddef

    def testAdd(self):
        x = Size.new_from_bytes(8, 1)
        y = Size.new_from_bytes(16, 1)
        actual = x.add(y).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(8, -1)
        y = Size.new_from_bytes(16, 1)
        actual = x.add(y).get_bytes()
        expected = (8, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(8, -1)
        y = Size.new_from_bytes(16, -1)
        actual = x.add(y).get_bytes()
        expected = (24, -1)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(0, 0)
        y = Size.new_from_bytes(16, -1)
        actual = x.add(y).get_bytes()
        expected = (16, -1)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(0, 0)
        y = Size.new_from_bytes(0, 0)
        actual = x.add(y).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef


    def testAddBytes(self):
        x = Size.new_from_bytes(8, 1)
        actual = x.add_bytes(16).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(8, -1)
        actual = x.add_bytes(8).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(8, -1)
        actual = x.add_bytes(0).get_bytes()
        expected = (8, -1)
        self.assertEqual(actual, expected)
    #enddef

    def testSub(self):
        x = Size.new_from_bytes(8, 1)
        y = Size.new_from_bytes(16, 1)
        actual = x.sub(y).get_bytes()
        expected = (8, -1)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(8, -1)
        y = Size.new_from_bytes(16, 1)
        actual = x.sub(y).get_bytes()
        expected = (24, -1)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(8, -1)
        y = Size.new_from_bytes(16, -1)
        actual = x.sub(y).get_bytes()
        expected = (8, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(0, 0)
        y = Size.new_from_bytes(16, -1)
        actual = x.sub(y).get_bytes()
        expected = (16, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(0, 0)
        y = Size.new_from_bytes(0, 0)
        actual = x.sub(y).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef

    def testSubBytes(self):
        x = Size.new_from_bytes(8, 1)
        actual = x.sub_bytes(16).get_bytes()
        expected = (8, -1)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(8, 1)
        actual = x.sub_bytes(8).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        x = Size.new_from_bytes(8, -1)
        actual = x.sub_bytes(0).get_bytes()
        expected = (8, -1)
        self.assertEqual(actual, expected)
    #enddef

    def testCmp(self):
        x = Size.new_from_str("1 KiB")
        y = Size.new_from_str("-1 KiB")

        # params: Size x, Size y, bool abs
        # result > 0
        cmpResult = Size.cmp(x, y, False)
        self.assertGreater(cmpResult, 0)

        # result < 0
        cmpResult = Size.cmp(y, x, False)
        self.assertLess(cmpResult, 0)

        # result == 0
        cmpResult = Size.cmp(y, x, True)
        self.assertEqual(cmpResult, 0)
    #enddef

    def testCmpBytes(self):
        x = Size.new_from_str("1 KiB")

        # result > 0
        y = 1023
        cmpResult = Size.cmp_bytes(x, y, False)
        self.assertGreater(cmpResult, 0)

        # result < 0
        y = 1025
        cmpResult = Size.cmp_bytes(x, y, False)
        self.assertLess(cmpResult, 0)

        # result == 0
        y = 1024
        cmpResult = Size.cmp_bytes(x, y, False)
        self.assertEqual(cmpResult, 0)

        # test with abs == True
        x = Size.new_from_str("-1 KiB")

        # result > 0
        y = 1023
        cmpResult = Size.cmp_bytes(x, y, True)
        self.assertGreater(cmpResult, 0)

        # result < 0
        y = 1025
        cmpResult = Size.cmp_bytes(x, y, True)
        self.assertLess(cmpResult, 0)

        # result == 0
        y = 1024
        cmpResult = Size.cmp_bytes(x, y, True)
        self.assertEqual(cmpResult, 0)
    #enddef

    def testConvertTo(self):
        x = Size.new_from_str("1 KiB")
        x.convert_to(ByteSize.Bunit.KIB)
    #enddef

    def testDiv(self):
        x = Size.new_from_str("1 KiB")
        y = Size.new_from_str("-0.1 KiB")
        divResult = x.div(y)
        self.assertEqual(divResult, 10)

        x = Size.new_from_str("1 MiB")
        y = Size.new_from_str("1 KiB")
        divResult = x.div(y)
        self.assertEqual(divResult, 1024)

        x = Size.new_from_str("1 GB")
        y = Size.new_from_str("0.7 GB")
        divResult = x.div(y)
        self.assertEqual(divResult, 1)

        x = Size.new_from_str("-1 KiB")
        y = Size.new_from_str("0.1 KiB")
        divResult = x.div(y)
        self.assertEqual(divResult, 10)
    #enddef

    def testDivInt(self):
        x = Size.new_from_str("1 MiB")
        y = 1024
        divResult = x.div_int(y).get_bytes()
        self.assertEqual(divResult, (1024, 1))

        # TODO currently fails, uncomment (fixed in new version)
        #x = Size.new_from_str("-1 MiB")
        #y = 1077
        #divResult = x.div_int(y).get_bytes()
        #self.assertEqual(divResult, (973, 1))
    #enddef

    def testGetBytesStr(self):
        strSize = Size.new_from_str("-1 KiB").get_bytes_str()
        self.assertEqual(strSize, "-1024")
    #enddef

    def testHumanReadable(self):
        strSize = Size.new_from_str("12 KiB").human_readable(ByteSize.Bunit.KIB, 2, True)
        self.assertEqual(strSize, "12 KiB")

        strSize = Size.new_from_str("1 KB").human_readable(ByteSize.Bunit.KIB, 2, False)
        self.assertEqual(strSize, "0.98 KiB")
    #enddef

    def testSgn(self):
        sgn = Size.new_from_str("12 KiB").sgn()
        self.assertEqual(sgn, 1)

        sgn = Size.new_from_str("0 MB").sgn()
        self.assertEqual(sgn, 0)

        sgn = Size.new_from_str("-12 GiB").sgn()
        self.assertEqual(sgn, -1)
    #enddef

    def testTrueDiv(self):
        x = Size.new_from_str("1024 B")
        y = Size.new_from_str("-102.4 B") # rounds to whole bytes
        divResult = float(x.true_div(y)[:15]) # just some number to cover accurancy and not cross max float range
        self.assertAlmostEqual(divResult, 1024/-102)

        x = Size.new_from_str("1 MiB")
        y = Size.new_from_str("1 KiB")
        divResult = float(x.true_div(y)[:15]) # just some number to cover accurancy and not cross max float range
        self.assertAlmostEqual(divResult, 1024.0)
    #enddef

    def testMod(self):
        x = Size.new_from_str("1024 B")
        y = Size.new_from_str("1000 B")
        actual = x.mod(y).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        # when modding the signs are ignored

        x = Size.new_from_str("1024 B")
        y = Size.new_from_str("-1000 B")
        actual = x.mod(y).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_str("-1024 B")
        y = Size.new_from_str("1000 B")
        actual = x.mod(y).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_str("-1024 B")
        y = Size.new_from_str("-1000 B")
        actual = x.mod(y).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_str("1024 B")
        y = Size.new_from_str("1024 B")
        actual = x.mod(y).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef

    def testMulFloatStr(self):
        x = Size.new_from_str("8 B")
        actual = x.mul_float_str("1.51").get_bytes()
        self.assertEqual(actual, (12, 1))

        x = Size.new_from_str("-8 B")
        actual = x.mul_float_str("1.51").get_bytes()
        self.assertEqual(actual, (12, -1))

        x = Size.new_from_str("8 B")
        actual = x.mul_float_str("-1.51").get_bytes()
        self.assertEqual(actual, (12, -1))
    #enddef

    def testMulInt(self):
        x = Size.new_from_str("8 B")
        y = 2
        actual = x.mul_int(y).get_bytes()
        expected = (16, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_str("0 B")
        y = 1
        actual = x.mul_int(y).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        x = Size.new_from_str("10 B")
        y = 0
        actual = x.mul_int(y).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef

    def testRoundToNearest(self):
        x = Size.new_from_str("1500 B")
        roundTo = Size.new_from_str("1 KiB")
        actual = x.round_to_nearest(roundTo, ByteSize.RoundDir.UP).get_bytes()
        expected = (2048, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_str("1500 B")
        roundTo = Size.new_from_str("1 KiB")
        actual = x.round_to_nearest(roundTo, ByteSize.RoundDir.DOWN).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)

        x = Size.new_from_str("1500 B")
        roundTo = Size.new_from_str("10 KiB")
        actual = x.round_to_nearest(roundTo, ByteSize.RoundDir.DOWN).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef

#endclass


# script entry point
if __name__=='__main__':
    unittest.main()
#endif

