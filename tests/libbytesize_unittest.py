#!/usr/bin/python3
# -*- coding: utf-8 -*-

import locale
import unittest
import sys
import ctypes

from locale_utils import get_avail_locales, missing_locales, requires_locales

from bytesize import KiB, GiB, ROUND_UP, ROUND_DOWN, ROUND_HALF_UP, OverflowError, InvalidSpecError

# SizeStruct is part of the 'private' API and needs to be imported differently
# when running from locally build tree and when using installed library
try:
    from bytesize import SizeStruct
except ImportError:
    from bytesize.bytesize import SizeStruct

DEFAULT_LOCALE = "en_US.utf8"

class SizeTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        unittest.TestCase.setUpClass()
        cls.avail_locales = get_avail_locales()

    def setUp(self):
        missing = missing_locales({DEFAULT_LOCALE}, self.avail_locales)
        if missing:
            self.skipTest("requires missing locales: %s" % missing)
        locale.setlocale(locale.LC_ALL, DEFAULT_LOCALE)
        self.addCleanup(self._clean_up)

    def _clean_up(self):
        locale.setlocale(locale.LC_ALL, DEFAULT_LOCALE)

    def testNew(self):
        actual = SizeStruct.new().get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)

    @requires_locales({'en_US.UTF-8'})
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

        # Regression test: "1. KiB" should parse successfully (existing behavior)
        # This is technically invalid (no digits after decimal point), but the
        # existing implementation accepts it, so we maintain backward compatibility.
        actual = SizeStruct.new_from_str('1. KiB').get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)

        # Regression test: "e+0" should raise InvalidSpecError (existing behavior)
        # This should not be parsed as 0, but should fail with an error.
        with self.assertRaises(InvalidSpecError):
            SizeStruct.new_from_str('e+0')

    @requires_locales({'cs_CZ.UTF-8'})
    def testNewFromStrLocaleCsCZ(self):
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

    @requires_locales({'ps_AF.UTF-8'})
    def testNewFromStrLocalePsAF(self):
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

        # now let's try something bigger than MAXUINT32
        actual = SizeStruct.new_from_bytes(5718360*1024, 1).get_bytes()
        expected = (5718360*1024, 1)
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

        # try some big value (bigger than ULONG_MAX on 32bit arches)
        x = SizeStruct.new_from_bytes(0, 0)
        actual = x.add_bytes(2**36).get_bytes()
        expected = (2**36, 1)
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

        # try some big value (bigger than ULONG_MAX on 32bit arches)
        x = SizeStruct.new_from_bytes(2**36 + 10, 1)
        actual = x.sub_bytes(2**36).get_bytes()
        expected = (10, 1)
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

        try:
            x = SizeStruct.new_from_bytes(2 * 2**36, 1)
            y = 2**36
            res = x.div_int(y).get_bytes()
            self.assertEqual(res, (2, 1))
        except OverflowError:
            # ULONG_MAX is the real limit for division, if it's smaller than
            # UINT64_MAX, an error is expected, otherwise it is a bug
            if ctypes.sizeof(ctypes.c_ulong) == 4:
                pass
    #enddef

    def testGetBytesStr(self):
        strSizeStruct = SizeStruct.new_from_str("-1 KiB").get_bytes_str()
        self.assertEqual(strSizeStruct, "-1024")
    #enddef

    def testHumanReadable(self):
        strSizeStruct = SizeStruct.new_from_str("12 KiB").human_readable(KiB, 2, False)
        self.assertEqual(strSizeStruct, "12 KiB")

        strSizeStruct = SizeStruct.new_from_str("1 KB").human_readable(KiB, 2, False)
        self.assertEqual(strSizeStruct, "0.98 KiB")

        strSizeStruct = SizeStruct.new_from_str("100 GiB").human_readable(KiB, 2, False)
        self.assertEqual(strSizeStruct, "100 GiB")

        strSizeStruct = SizeStruct.new_from_str("100.00 GiB").human_readable(KiB, 2, False)
        self.assertEqual(strSizeStruct, "100 GiB")

        strSizeStruct = SizeStruct.new_from_str("100 GiB").human_readable(KiB, 0, False)
        self.assertEqual(strSizeStruct, "100 GiB")

        # test that the result of human_readable() can be parsed back
        strSizeStruct = SizeStruct.new_from_str("100 GiB").human_readable(GiB, 0, False)
        self.assertEqual(SizeStruct.new_from_str(strSizeStruct).get_bytes(), (100 * 1024**3, 1))

        # even if translated
        strSizeStruct = SizeStruct.new_from_str("100 GiB").human_readable(GiB, 0, True)
        self.assertEqual(SizeStruct.new_from_str(strSizeStruct).get_bytes(), (100 * 1024**3, 1))
    #enddef

    @requires_locales({'cs_CZ.UTF-8'})
    def testHumanReadableLocale(self):
        locale.setlocale(locale.LC_ALL, 'cs_CZ.UTF-8')
        strSizeStruct = SizeStruct.new_from_str("1 KB").human_readable(KiB, 2, True)
        self.assertEqual(strSizeStruct, "0,98 KiB")
        locale.setlocale(locale.LC_ALL, DEFAULT_LOCALE);

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
        divResult = float(x.true_div(y)[:15].replace(locale.nl_langinfo(locale.RADIXCHAR), ".")) # just some number to cover accurancy and not cross max float range
        self.assertAlmostEqual(divResult, 1024.0/-102.0)

        x = SizeStruct.new_from_str("1 MiB")
        y = SizeStruct.new_from_str("1 KiB")
        divResult = float(x.true_div(y)[:15].replace(locale.nl_langinfo(locale.RADIXCHAR), ".")) # just some number to cover accurancy and not cross max float range
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

        x = SizeStruct.new_from_bytes(4, 1)
        y = 2**36
        actual = x.mul_int(y).get_bytes()
        expected = (4 * 2**36, 1)
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

        x = SizeStruct.new_from_str("1024 B")
        roundTo = SizeStruct.new_from_str("1 KiB")
        actual = x.round_to_nearest(roundTo, ROUND_DOWN).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)
        actual = x.round_to_nearest(roundTo, ROUND_UP).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)
        actual = x.round_to_nearest(roundTo, ROUND_HALF_UP).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("1023 B")
        actual = x.round_to_nearest(roundTo, ROUND_DOWN).get_bytes()
        expected = (0, 0)
        self.assertEqual(actual, expected)
        actual = x.round_to_nearest(roundTo, ROUND_UP).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)
        actual = x.round_to_nearest(roundTo, ROUND_HALF_UP).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("1025 B")
        actual = x.round_to_nearest(roundTo, ROUND_DOWN).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)
        actual = x.round_to_nearest(roundTo, ROUND_UP).get_bytes()
        expected = (2048, 1)
        self.assertEqual(actual, expected)
        actual = x.round_to_nearest(roundTo, ROUND_HALF_UP).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("1535 B")
        actual = x.round_to_nearest(roundTo, ROUND_DOWN).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)
        actual = x.round_to_nearest(roundTo, ROUND_UP).get_bytes()
        expected = (2048, 1)
        self.assertEqual(actual, expected)
        actual = x.round_to_nearest(roundTo, ROUND_HALF_UP).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("1536 B")
        actual = x.round_to_nearest(roundTo, ROUND_DOWN).get_bytes()
        expected = (1024, 1)
        self.assertEqual(actual, expected)
        actual = x.round_to_nearest(roundTo, ROUND_UP).get_bytes()
        expected = (2048, 1)
        self.assertEqual(actual, expected)
        actual = x.round_to_nearest(roundTo, ROUND_HALF_UP).get_bytes()
        expected = (2048, 1)
        self.assertEqual(actual, expected)

        # now check something bigger
        x = SizeStruct.new_from_str("575 GiB")
        roundTo = SizeStruct.new_from_str("128 GiB")
        actual = x.round_to_nearest(roundTo, ROUND_HALF_UP).get_bytes_str()
        expected = SizeStruct.new_from_str("512 GiB").get_bytes_str()
        self.assertEqual(actual, expected)

        x = SizeStruct.new_from_str("576 GiB")
        roundTo = SizeStruct.new_from_str("128 GiB")
        actual = x.round_to_nearest(roundTo, ROUND_HALF_UP).get_bytes_str()
        expected = SizeStruct.new_from_str("640 GiB").get_bytes_str()
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

        x = SizeStruct.new_from_bytes(16, 1)
        x.grow_bytes(2**36)
        actual = x.get_bytes()
        expected = (16 + 2**36, 1)
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

        x = SizeStruct.new_from_bytes(4, 1)
        x.grow_mul_int(2**36)
        actual = x.get_bytes()
        expected = (4 * 2**36, 1)
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

        x = SizeStruct.new_from_bytes(2 * 2**36, 1)
        x.shrink_bytes(2**36)
        actual = x.get_bytes()
        expected = (2**36, 1)
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

        x = SizeStruct.new_from_bytes(2 * 2**36, 1)
        y = 2**36
        try:
            res = x.shrink_div_int(y).get_bytes()
            self.assertEqual(res, (2, 1))
        except OverflowError:
            # ULONG_MAX is the real limit for division, if it's smaller than
            # UINT64_MAX, an error is expected, otherwise it is a bug
            if ctypes.sizeof(ctypes.c_ulong) == 4:
                pass
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

        x = SizeStruct.new_from_bytes(10 * 2**36, 1)
        y = 2**36
        try:
            res = float(x.true_div_int(y)[:15])
            self.assertAlmostEqual(res, 10.0)
        except OverflowError:
            # ULONG_MAX is the real limit for division, if it's smaller than
            # UINT64_MAX, an error is expected, otherwise it is a bug
            if ctypes.sizeof(ctypes.c_ulong) == 4:
                pass
    #enddef

    @requires_locales({'en_US.UTF-8'})
    def testPowerComputationRoundingIssues(self):
        """Test cases that expose rounding differences when using floating-point arithmetic.
        
        These test cases were discovered by fuzzing and demonstrate that both GMP and MPFR 
        can produce incorrect results due to floating-point rounding errors: half of these
        fail using GMP floating-point arithmetic, and half fail using MPFR floating-point
        arithmetic. They all pass using rational arithmetic, so this can be considered a
        regression test against parsing decimal strings into floats.
        """
        # Test cases: (input_string, expected_bytes)
        test_cases = [
            # Small values with various powers
            ('0.0011085865 EB', 1108586500000000),
            ('0.0021209044 TB', 2120904400),
            ('0.0022392293 EB', 2239229300000000),
            ('0.0022951087 YB', 2295108700000000000000),
            ('0.0040214632 YB', 4021463200000000000000),
            ('0.0041468690 YB', 4146869000000000000000),
            ('0.0042571596 ZB', 4257159600000000000),
            ('0.0042875429 EB', 4287542900000000),
            ('0.0324645967 YB', 32464596700000000000000),
            ('0.1417885628 ZB', 141788562800000000000),
            
            # Medium values
            ('1.2558302853 TB', 1255830285300),
            ('1.2808632839 TB', 1280863283900),
            ('1.4603574651 TB', 1460357465100),
            ('1.8062283468 ZB', 1806228346800000000000),
            ('1.8645823412 YB', 1864582341200000000000000),
            ('1.9238933576 ZB', 1923893357600000000000),
            ('1.9665143540 YB', 1966514354000000000000000),
            ('2.2322652035 TB', 2232265203500),
            ('2.2791207143 EB', 2279120714300000000),
            ('2.6701042923 YB', 2670104292300000000000000),
            ('2.7289885652 ZB', 2728988565200000000000),
            ('2.7544584366 PB', 2754458436600000),
            ('3.0111054820 GB', 3011105482),
            ('3.0162065825 YB', 3016206582500000000000000),
            ('3.0843591206 ZB', 3084359120600000000000),
            ('3.1113231336 ZB', 3111323133600000000000),
            ('3.1515752061 PB', 3151575206100000),
            ('3.5209720810 YB', 3520972081000000000000000),
            ('4.8518650436 TB', 4851865043600),
            ('5.2369996109 TB', 5236999610900),
            ('5.3013442478 ZB', 5301344247800000000000),
            ('5.7581197108 YB', 5758119710800000000000000),
            ('6.3559455332 TB', 6355945533200),
            ('6.7238548658 ZB', 6723854865800000000000),
            ('6.8329986622 YB', 6832998662200000000000000),
            ('6.8908620007 EB', 6890862000700000000),
            ('7.0261924059 PB', 7026192405900000),
            ('7.0606267555 PB', 7060626755500000),
            ('7.0944972810 PB', 7094497281000000),
            ('7.3977189826 PB', 7397718982600000),
            ('7.4709433968 EB', 7470943396800000000),
            ('8.3657937505 TB', 8365793750500),
            ('8.4406057674 ZB', 8440605767400000000000),
            ('8.4870627422 PB', 8487062742200000),
            ('8.7299932796 PB', 8729993279600000),
            ('9.3673512126 PB', 9367351212600000),
            ('9.5884958998 ZB', 9588495899800000000000),
            ('12.6938536209 EB', 12693853620900000000),
            ('12.9715312556 PB', 12971531255600000),
            ('13.9278925503 YB', 13927892550300000000000000),
            ('16.5366973188 EB', 16536697318800000000),
            ('16.8402344837 TB', 16840234483700),
            ('18.1701051043 YB', 18170105104300000000000000),
            ('20.8472056786 PB', 20847205678600000),
            ('23.4774112918 TB', 23477411291800),
            ('24.5449421357 ZB', 24544942135700000000000),
            ('28.2128860554 YB', 28212886055400000000000000),
            ('29.8952920687 EB', 29895292068700000000),
            ('35.2174130896 TB', 35217413089600),
            ('35.4501743352 EB', 35450174335200000000),
            ('35.8588722037 ZB', 35858872203700000000000),
            ('39.8097589703 TB', 39809758970300),
            ('41.9150701874 ZB', 41915070187400000000000),
            ('76.8145331495 YB', 76814533149500000000000000),
            ('85.3995925075 PB', 85399592507500000),
            ('87.1440005221 YB', 87144000522100000000000000),
            ('87.3254482326 PB', 87325448232600000),
            ('98.2498190219 EB', 98249819021900000000),
            ('128.1037376252 PB', 128103737625200000),
            ('130.4743561323 ZB', 130474356132300000000000),
            ('138.2867513494 YB', 138286751349400000000000000),
            
            # Large values
            ('18258.0630890156 PB', 18258063089015600000),
            ('18800.1176214700 EB', 18800117621470000000000),
            ('269636.0318459886 YB', 269636031845988600000000000000),
            ('276686.6833125990 YB', 276686683312599000000000000000),
            ('535817.4105711933 EB', 535817410571193300000000),
        ]
        
        for test_str, expected_bytes in test_cases:
            with self.subTest(test_str=test_str):
                size = SizeStruct.new_from_str(test_str)
                # Check if value exceeds 64-bit integer limit
                if expected_bytes > 2**64 - 1:
                    # Use get_bytes_str() for values that exceed 64-bit limit
                    actual_str = size.get_bytes_str()
                    expected_str = str(expected_bytes)
                    self.assertEqual(actual_str, expected_str,
                        f'Failed for {test_str}: got {actual_str}, expected {expected_str}')
                else:
                    actual = size.get_bytes()
                    expected = (expected_bytes, 1)
                    self.assertEqual(actual, expected,
                        f'Failed for {test_str}: got {actual}, expected {expected}')

    #enddef

#endclass


# script entry point
if __name__=='__main__':
    if len(sys.argv) > 1:
        DEFAULT_LOCALE = sys.argv[1]
        # the unittest module would try to intepret the argument too, let's
        # remove it
        sys.argv = [sys.argv[0]]
    unittest.main()
#endif
