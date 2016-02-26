#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import locale
import unittest

from bytesize import SizeStruct, KiB, ROUND_UP, ROUND_DOWN

class SizeTestCase(unittest.TestCase):

    def testNew(self):
        actual = SizeStruct.new().get_bytes()
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
        actual = SizeStruct.new_from_str('0 B').get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('1 KiB').get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('1KB').get_bytes()
        expected = (1000, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('1 MiB').get_bytes()
        expected = (1048576, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('   1 MiB').get_bytes()
        expected = (1048576, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('1 MiB    ').get_bytes()
        expected = (1048576, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('    1 MiB   ').get_bytes()
        expected = (1048576, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('-1.5 GiB').get_bytes()
        expected = (1610612736, -1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('+1.5 GiB').get_bytes()
        expected = (1610612736, 1)
        self.assertEqual(actual, expected)

        locale.setlocale(locale.LC_ALL,'cs_CZ.UTF-8')

        actual = SizeStruct.new_from_str('1,5 KiB').get_bytes()
        expected = (1536, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('-1,5 KiB').get_bytes()
        expected = (1536, -1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('1.5 KiB').get_bytes()
        expected = (1536, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('-1.5 KiB').get_bytes()
        expected = (1536, -1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('1e-1 KB').get_bytes()
        expected = (100, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('-1e-1 KB').get_bytes()
        expected = (100, -1)
        self.assertEqual(actual, expected)

        # this persian locale uses a two-byte unicode character for the radix
        locale.setlocale(locale.LC_ALL, 'ps_AF.UTF-8')

        actual = SizeStruct.new_from_str('1٫5 KiB').get_bytes()
        expected = (1536, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('-1٫5 KiB').get_bytes()
        expected = (1536, -1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('1.5 KiB').get_bytes()
        expected = (1536, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_str('-1.5 KiB').get_bytes()
        expected = (1536, -1)
        self.assertEqual(actual, expected)

        locale.setlocale(locale.LC_ALL,'en_US.UTF-8')

    #enddef

    def testNewFromBytes(self):
        actual = SizeStruct.new_from_bytes(0, 0).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_bytes(10, 1).get_bytes()
        expected = (10, 1)
        self.assertEqual(actual, expected)

        actual = SizeStruct.new_from_bytes(1024, -1).get_bytes()
        expected = (1024, -1)
        self.assertEqual(actual, expected)
    #enddef

    def testNewFromSizeStruct(self):
        tempSizeStruct = SizeStruct.new_from_bytes(17, 1)
        actual = SizeStruct.new_from_size(tempSizeStruct).get_bytes()
        expected = (17, 1)
        self.assertEqual(actual, expected)
    #enddef

    def testAdd(self):
        x = SizeStruct.new_from_bytes(8, 1)
        y = SizeStruct.new_from_bytes(16, 1)
        actual = x.add(y).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(8, -1)
        y = SizeStruct.new_from_bytes(16, 1)
        actual = x.add(y).get_bytes()
        expected = (8, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(8, -1)
        y = SizeStruct.new_from_bytes(16, -1)
        actual = x.add(y).get_bytes()
        expected = (24, -1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(0, 0)
        y = SizeStruct.new_from_bytes(16, -1)
        actual = x.add(y).get_bytes()
        expected = (16, -1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(0, 0)
        y = SizeStruct.new_from_bytes(0, 0)
        actual = x.add(y).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef


    def testAddBytes(self):
        x = SizeStruct.new_from_bytes(8, 1)
        actual = x.add_bytes(16).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(8, -1)
        actual = x.add_bytes(8).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(8, -1)
        actual = x.add_bytes(0).get_bytes()
        expected = (8, -1)
        self.assertEqual(actual, expected)
    #enddef

    def testSub(self):
        x = SizeStruct.new_from_bytes(8, 1)
        y = SizeStruct.new_from_bytes(16, 1)
        actual = x.sub(y).get_bytes()
        expected = (8, -1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(8, -1)
        y = SizeStruct.new_from_bytes(16, 1)
        actual = x.sub(y).get_bytes()
        expected = (24, -1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(8, -1)
        y = SizeStruct.new_from_bytes(16, -1)
        actual = x.sub(y).get_bytes()
        expected = (8, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(0, 0)
        y = SizeStruct.new_from_bytes(16, -1)
        actual = x.sub(y).get_bytes()
        expected = (16, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(0, 0)
        y = SizeStruct.new_from_bytes(0, 0)
        actual = x.sub(y).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef

    def testSubBytes(self):
        x = SizeStruct.new_from_bytes(8, 1)
        actual = x.sub_bytes(16).get_bytes()
        expected = (8, -1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(8, 1)
        actual = x.sub_bytes(8).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(8, -1)
        actual = x.sub_bytes(0).get_bytes()
        expected = (8, -1)
        self.assertEqual(actual, expected)
    #enddef

    def testCmp(self):
        x = SizeStruct.new_from_str("1 KiB")
        y = SizeStruct.new_from_str("-1 KiB")

        # params: SizeStruct x, SizeStruct y, bool abs
        # result > 0
        cmpResult = SizeStruct.cmp(x, y, False)
        self.assertGreater(cmpResult, 0)

        # result < 0
        cmpResult = SizeStruct.cmp(y, x, False)
        self.assertLess(cmpResult, 0)

        # result == 0
        cmpResult = SizeStruct.cmp(y, x, True)
        self.assertEqual(cmpResult, 0)
    #enddef

    def testCmpBytes(self):
        x = SizeStruct.new_from_str("1 KiB")

        # result > 0
        y = 1023
        cmpResult = SizeStruct.cmp_bytes(x, y, False)
        self.assertGreater(cmpResult, 0)

        # result < 0
        y = 1025
        cmpResult = SizeStruct.cmp_bytes(x, y, False)
        self.assertLess(cmpResult, 0)

        # result == 0
        y = 1024
        cmpResult = SizeStruct.cmp_bytes(x, y, False)
        self.assertEqual(cmpResult, 0)

        # test with abs == True
        x = SizeStruct.new_from_str("-1 KiB")

        # result > 0
        y = 1023
        cmpResult = SizeStruct.cmp_bytes(x, y, True)
        self.assertGreater(cmpResult, 0)

        # result < 0
        y = 1025
        cmpResult = SizeStruct.cmp_bytes(x, y, True)
        self.assertLess(cmpResult, 0)

        # result == 0
        y = 1024
        cmpResult = SizeStruct.cmp_bytes(x, y, True)
        self.assertEqual(cmpResult, 0)
    #enddef

    def testConvertTo(self):
        x = SizeStruct.new_from_str("1 KiB")
        x.convert_to(KiB)
    #enddef

    def testDiv(self):
        x = SizeStruct.new_from_str("1 KiB")
        y = SizeStruct.new_from_str("-0.1 KiB")
        divResult = x.div(y)
        self.assertEqual(divResult, (10, -1))

        x = SizeStruct.new_from_str("1 MiB")
        y = SizeStruct.new_from_str("1 KiB")
        divResult = x.div(y)
        self.assertEqual(divResult, (1024, 1))

        x = SizeStruct.new_from_str("1 GB")
        y = SizeStruct.new_from_str("0.7 GB")
        divResult = x.div(y)
        self.assertEqual(divResult, (1, 1))

        x = SizeStruct.new_from_str("-1 KiB")
        y = SizeStruct.new_from_str("0.1 KiB")
        divResult = x.div(y)
        self.assertEqual(divResult, (10, -1))
    #enddef

    def testDivInt(self):
        x = SizeStruct.new_from_str("1 MiB")
        y = 1024
        divResult = x.div_int(y).get_bytes()
        self.assertEqual(divResult, (1024, 1))

        x = SizeStruct.new_from_str("-1 MiB")
        y = 1077
        divResult = x.div_int(y).get_bytes()
        self.assertEqual(divResult, (973, -1))
    #enddef

    def testGetBytesStr(self):
        strSizeStruct = SizeStruct.new_from_str("-1 KiB").get_bytes_str()
        self.assertEqual(strSizeStruct, "-1024")
    #enddef

    def testHumanReadable(self):
        strSizeStruct = SizeStruct.new_from_str("12 KiB").human_readable(KiB, 2, True)
        self.assertEqual(strSizeStruct, "12 KiB")

        strSizeStruct = SizeStruct.new_from_str("1 KB").human_readable(KiB, 2, False)
        self.assertEqual(strSizeStruct, "0.98 KiB")

        strSizeStruct = SizeStruct.new_from_str("100 GiB").human_readable(KiB, 2, False)
        self.assertEqual(strSizeStruct, "100 GiB")

        strSizeStruct = SizeStruct.new_from_str("100.00 GiB").human_readable(KiB, 2, False)
        self.assertEqual(strSizeStruct, "100 GiB")

        strSizeStruct = SizeStruct.new_from_str("100 GiB").human_readable(KiB, 0, False)
        self.assertEqual(strSizeStruct, "100 GiB")
    #enddef

    def testSgn(self):
        sgn = SizeStruct.new_from_str("12 KiB").sgn()
        self.assertEqual(sgn, 1)

        sgn = SizeStruct.new_from_str("0 MB").sgn()
        self.assertEqual(sgn, 0)

        sgn = SizeStruct.new_from_str("-12 GiB").sgn()
        self.assertEqual(sgn, -1)
    #enddef

    def testTrueDiv(self):
        x = SizeStruct.new_from_str("1024 B")
        y = SizeStruct.new_from_str("-102.4 B") # rounds to whole bytes
        divResult = float(x.true_div(y)[:15]) # just some number to cover accurancy and not cross max float range
        self.assertAlmostEqual(divResult, 1024.0/-102.0)

        x = SizeStruct.new_from_str("1 MiB")
        y = SizeStruct.new_from_str("1 KiB")
        divResult = float(x.true_div(y)[:15]) # just some number to cover accurancy and not cross max float range
        self.assertAlmostEqual(divResult, 1024.0)
    #enddef

    def testMod(self):
        x = SizeStruct.new_from_str("1024 B")
        y = SizeStruct.new_from_str("1000 B")
        actual = x.mod(y).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        # when modding the signs are ignored

        x = SizeStruct.new_from_str("1024 B")
        y = SizeStruct.new_from_str("-1000 B")
        actual = x.mod(y).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("-1024 B")
        y = SizeStruct.new_from_str("1000 B")
        actual = x.mod(y).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("-1024 B")
        y = SizeStruct.new_from_str("-1000 B")
        actual = x.mod(y).get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("1024 B")
        y = SizeStruct.new_from_str("1024 B")
        actual = x.mod(y).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef

    def testMulFloatStr(self):
        x = SizeStruct.new_from_str("8 B")
        actual = x.mul_float_str("1.51").get_bytes()
        self.assertEqual(actual, (12, 1))

        x = SizeStruct.new_from_str("-8 B")
        actual = x.mul_float_str("1.51").get_bytes()
        self.assertEqual(actual, (12, -1))

        x = SizeStruct.new_from_str("8 B")
        actual = x.mul_float_str("-1.51").get_bytes()
        self.assertEqual(actual, (12, -1))
    #enddef

    def testMulInt(self):
        x = SizeStruct.new_from_str("8 B")
        y = 2
        actual = x.mul_int(y).get_bytes()
        expected = (16, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("0 B")
        y = 1
        actual = x.mul_int(y).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("10 B")
        y = 0
        actual = x.mul_int(y).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef

    def testRoundToNearest(self):
        x = SizeStruct.new_from_str("1500 B")
        roundTo = SizeStruct.new_from_str("1 KiB")
        actual = x.round_to_nearest(roundTo, ROUND_UP).get_bytes()
        expected = (2048, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("1500 B")
        roundTo = SizeStruct.new_from_str("1 KiB")
        actual = x.round_to_nearest(roundTo, ROUND_DOWN).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("1500 B")
        roundTo = SizeStruct.new_from_str("10 KiB")
        actual = x.round_to_nearest(roundTo, ROUND_DOWN).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef

    def testGrow(self):
        x = SizeStruct.new_from_bytes(16, 1)
        y = SizeStruct.new_from_bytes(8, 1)
        x.grow(y)
        actual = x.get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)
    #enddef

    def testGrowBytes(self):
        x = SizeStruct.new_from_bytes(16, 1)
        x.grow_bytes(8)
        actual = x.get_bytes()
        expected = (24, 1)
        self.assertEqual(actual, expected)
    #enddef

    def testGrowMulFloatStr(self):
        x = SizeStruct.new_from_str("8 B")
        x.grow_mul_float_str("1.51")
        actual = x.get_bytes()
        self.assertEqual(actual, (12, 1))

        x = SizeStruct.new_from_str("-8 B")
        x.grow_mul_float_str("1.51")
        actual = x.get_bytes()
        self.assertEqual(actual, (12, -1))

        x = SizeStruct.new_from_str("8 B")
        x.grow_mul_float_str("-1.51")
        actual = x.get_bytes()
        self.assertEqual(actual, (12, -1))
    #enddef

    def testGrowMulInt(self):
        x = SizeStruct.new_from_str("8 B")
        x.grow_mul_int(2)
        actual = x.get_bytes()
        expected = (16, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("0 B")
        x.grow_mul_int(1)
        actual = x.get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("10 B")
        x.grow_mul_int(0)
        actual = x.get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
    #enddef

    def testShrink(self):
        x = SizeStruct.new_from_bytes(16, 1)
        y = SizeStruct.new_from_bytes(8, 1)
        x.shrink(y)
        actual = x.get_bytes()
        expected = (8, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_bytes(8, 1)
        y = SizeStruct.new_from_bytes(16, 1)
        x.shrink(y)
        actual = x.get_bytes()
        expected = (8, -1)
        self.assertEqual(actual, expected)
    #enddef

    def testShrinkBytes(self):
        x = SizeStruct.new_from_str("8 B")
        x.shrink_bytes(2)
        actual = x.get_bytes()
        expected = (6, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("8 B")
        x.shrink_bytes(16)
        actual = x.get_bytes()
        expected = (8, -1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("-8 B")
        x.shrink_bytes(8)
        actual = x.get_bytes()
        expected = (16, -1)
        self.assertEqual(actual, expected)
    #enddef

    def testShrinkDivInt(self):
        x = SizeStruct.new_from_str("100 B")
        y = 11
        x.shrink_div_int(y)
        actual = x.get_bytes()
        expected = (9, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("98 B")
        y = 11
        x.shrink_div_int(y)
        actual = x.get_bytes()
        expected = (8, 1)
        self.assertEqual(actual, expected)
    #enddef

    def testTrueDivInt(self):
        x = SizeStruct.new_from_str("1000 B")
        y = 100
        divResult = float(x.true_div_int(y)[:15]) # just some number to cover accuracy and not cross max float range
        self.assertAlmostEqual(divResult, 1000.0/100.0)

        x = SizeStruct.new_from_str("-1 MiB")
        y = 1024
        divResult = float(x.true_div_int(y)[:15]) # just some number to cover accuracy and not cross max float range
        self.assertAlmostEqual(divResult, -1024.0)

        x = SizeStruct.new_from_str("0 MiB")
        y = 1024
        divResult = float(x.true_div_int(y)[:15]) # just some number to cover accuracy and not cross max float range
        self.assertAlmostEqual(divResult, 0.0)
    #enddef

#endclass


# script entry point
if __name__=='__main__':
    unittest.main()
#endif

