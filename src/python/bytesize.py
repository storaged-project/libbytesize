import ctypes
from ctypes import POINTER, byref

import six
from decimal import Decimal

import locale

import gettext
_ = lambda x: gettext.translation("libbytesize", fallback=True).gettext(x) if x != "" else ""

"""
Python bindings for the libbytesize library and it's BSSize "class". These
bindings provide a real Python class :class:`Size` which wraps the libbytesize
functionality and provides all the features one would expect from a numeric type
in Python.

.. note::
  ``None`` is treated as ``Size(0)`` in mathematical operations.

"""

c_bytesize = ctypes.CDLL("libbytesize.so.1")

B = 0
KiB = 1
MiB = 2
GiB = 3
TiB = 4
PiB = 5
EiB = 6
ZiB = 7
YiB = 8
KB = 21
MB = 22
GB = 23
TB = 24
PB = 25
EB = 26
ZB = 27
YB = 28

ROUND_UP = 0
ROUND_DOWN = 1
ROUND_HALF_UP = 2

MAXUINT64 = 2**64 - 1

unit_strs = {
    "B": B, "KiB": KiB, "MiB": MiB, "GiB": GiB, "TiB": TiB, "PiB": PiB, "EiB": EiB, "ZiB": ZiB, "YiB": YiB,
    "KB": KB, "MB": MB, "GB": GB, "TB": TB, "PB": PB, "EB": EB, "ZB": ZB, "YB": YB,
    }

def unit_str(unit, xlate=False):
    for (u_str, u) in unit_strs.items():
        if u == unit:
            return _(u_str) if xlate else u_str

class SizeErrorStruct(ctypes.Structure):
    _fields_ = [("code", ctypes.c_int),
                ("msg", ctypes.c_char_p)]

class SizeError(Exception):
    pass

class InvalidSpecError(SizeError):
    pass

class OverflowError(SizeError):
    pass

class ZeroDivisionError(SizeError):
    pass

_error_code_clss = (InvalidSpecError, OverflowError, ZeroDivisionError)

def get_error(err):
    if not err:
        return None
    if six.PY3:
        msg = str(err.contents.msg, "utf-8")
    else:
        msg = err.contents.msg
    ex = _error_code_clss[err.contents.code](msg)
    c_bytesize.bs_clear_error(byref(err))
    raise ex

class SizeStruct(ctypes.Structure):
    @classmethod
    def new(cls):
        return c_bytesize.bs_size_new().contents

    @classmethod
    def new_from_bytes(cls, byts, sgn):
        return c_bytesize.bs_size_new_from_bytes(byts, sgn).contents

    @classmethod
    def new_from_str(cls, s):
        err = POINTER(SizeErrorStruct)()
        if six.PY3:
            s = bytes(s, "utf-8")
        ret = c_bytesize.bs_size_new_from_str(s, byref(err))
        get_error(err)
        return ret.contents

    @classmethod
    def new_from_size(cls, sz):
        return c_bytesize.bs_size_new_from_size(sz).contents

    def __del__(self):
        # XXX: For some reason c_bytesize may be None here (probably when python
        #      cleans up after itself) and loading it again doesn't work at that
        #      stage. Let's just prevent ignored exceptions from happening.
        if c_bytesize:
            c_bytesize.bs_size_free(self)

    def get_bytes(self):
        sgn = ctypes.c_int(0)
        err = POINTER(SizeErrorStruct)()
        ret = c_bytesize.bs_size_get_bytes(self, byref(sgn), byref(err))
        get_error(err)
        return (ret, sgn.value)

    def get_bytes_str(self):
        if six.PY3:
            return str(c_bytesize.bs_size_get_bytes_str(self), "utf-8")
        else:
            return c_bytesize.bs_size_get_bytes_str(self)

    def add(self, sz):
        return c_bytesize.bs_size_add(self, sz).contents

    def add_bytes(self, b):
        return c_bytesize.bs_size_add_bytes(self, b).contents

    def grow(self, sz):
        c_bytesize.bs_size_grow(self, sz)
        return self

    def grow_bytes(self, b):
        c_bytesize.bs_size_grow_bytes(self, b)
        return self

    def sub(self, sz):
        return c_bytesize.bs_size_sub(self, sz).contents

    def sub_bytes(self, b):
        return c_bytesize.bs_size_sub_bytes(self, b).contents

    def shrink(self, sz):
        c_bytesize.bs_size_shrink(self, sz)
        return self

    def shrink_bytes(self, b):
        c_bytesize.bs_size_shrink_bytes(self, b)
        return self

    def cmp(self, sz, ign_sgn):
        return c_bytesize.bs_size_cmp(self, sz, ign_sgn)

    def cmp_bytes(self, b, ign_sgn):
        return c_bytesize.bs_size_cmp_bytes(self, b, ign_sgn)

    def convert_to(self, unit):
        err = POINTER(SizeErrorStruct)()
        ret = c_bytesize.bs_size_convert_to(self, unit, byref(err))
        get_error(err)
        if six.PY3:
            ret = str(ret, "utf-8")
        return ret

    def div(self, sz):
        sgn = ctypes.c_int(0)
        err = POINTER(SizeErrorStruct)()
        ret = c_bytesize.bs_size_div(self, sz, byref(sgn), byref(err))
        get_error(err)
        return (ret, sgn.value)

    def div_int(self, div):
        err = POINTER(SizeErrorStruct)()
        ret = c_bytesize.bs_size_div_int(self, div, byref(err))
        get_error(err)
        return ret.contents

    def shrink_div_int(self, div):
        err = POINTER(SizeErrorStruct)()
        c_bytesize.bs_size_shrink_div_int(self, div, byref(err))
        get_error(err)
        return self

    def human_readable(self, min_unit, max_places, xlate):
        if six.PY3:
            return str(c_bytesize.bs_size_human_readable(self, min_unit, max_places, xlate), "utf-8")
        else:
            return c_bytesize.bs_size_human_readable(self, min_unit, max_places, xlate)

    def sgn(self):
        return c_bytesize.bs_size_sgn(self)

    def true_div(self, sz):
        err = POINTER(SizeErrorStruct)()
        ret = c_bytesize.bs_size_true_div(self, sz, byref(err))
        get_error(err)
        if six.PY3:
            ret = str(ret, "utf-8")
        return ret

    def true_div_int(self, div):
        err = POINTER(SizeErrorStruct)()
        ret = c_bytesize.bs_size_true_div_int(self, div, byref(err))
        get_error(err)
        if six.PY3:
            ret = str(ret, "utf-8")
        return ret

    def mod(self, sz):
        err = POINTER(SizeErrorStruct)()
        ret = c_bytesize.bs_size_mod(self, sz, byref(err))
        get_error(err)
        return ret.contents

    def mul_float_str(self, fl_str):
        err = POINTER(SizeErrorStruct)()
        if six.PY3:
            fl_str = bytes(fl_str, "utf-8")
        ret = c_bytesize.bs_size_mul_float_str(self, fl_str, byref(err))
        get_error(err)
        return ret.contents

    def grow_mul_float_str(self, fl_str):
        err = POINTER(SizeErrorStruct)()
        if six.PY3:
            fl_str = bytes(fl_str, "utf-8")
        c_bytesize.bs_size_grow_mul_float_str(self, fl_str, byref(err))
        get_error(err)
        return self

    def mul_int(self, i):
        err = POINTER(SizeErrorStruct)()
        ret = c_bytesize.bs_size_mul_int(self, i)
        get_error(err)
        return ret.contents

    def grow_mul_int(self, i):
        err = POINTER(SizeErrorStruct)()
        c_bytesize.bs_size_grow_mul_int(self, i)
        get_error(err)
        return self

    def round_to_nearest(self, sz, dir):
        err = POINTER(SizeErrorStruct)()
        ret = c_bytesize.bs_size_round_to_nearest(self, sz, dir, byref(err))
        get_error(err)
        return ret.contents

    def __repr__(self):
        return "Size (%s)" % self.human_readable(B, -1, False)

## Constructors
c_bytesize.bs_size_new.restype = POINTER(SizeStruct)
c_bytesize.bs_size_new.argtypes = []
c_bytesize.bs_size_new_from_bytes.restype = POINTER(SizeStruct)
c_bytesize.bs_size_new_from_bytes.argtypes = [ctypes.c_ulonglong, ctypes.c_int]
c_bytesize.bs_size_new_from_str.restype = POINTER(SizeStruct)
c_bytesize.bs_size_new_from_str.argtypes = [ctypes.c_char_p, POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_new_from_size.restype = POINTER(SizeStruct)
c_bytesize.bs_size_new_from_size.argtypes = [POINTER(SizeStruct)]

## Destructors
c_bytesize.bs_size_free.restype = None
c_bytesize.bs_size_free.argtypes = [POINTER(SizeStruct)]
c_bytesize.bs_clear_error.restype = None
c_bytesize.bs_clear_error.argtypes = [POINTER(POINTER(SizeErrorStruct))]

## Query methods
c_bytesize.bs_size_get_bytes.restype = ctypes.c_ulonglong
c_bytesize.bs_size_get_bytes.argtypes = [POINTER(SizeStruct), POINTER(ctypes.c_int), POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_sgn.restype = ctypes.c_int
c_bytesize.bs_size_sgn.argtypes = [POINTER(SizeStruct)]
c_bytesize.bs_size_get_bytes_str.restype = ctypes.c_char_p
c_bytesize.bs_size_get_bytes_str.argtypes = [POINTER(SizeStruct)]
c_bytesize.bs_size_convert_to.restype = ctypes.c_char_p
c_bytesize.bs_size_convert_to.argtypes = [POINTER(SizeStruct), ctypes.c_int, POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_human_readable.restype = ctypes.c_char_p
c_bytesize.bs_size_human_readable.argtypes = [POINTER(SizeStruct), ctypes.c_int, ctypes.c_int, ctypes.c_bool]

## Arithmetic
c_bytesize.bs_size_add.restype = POINTER(SizeStruct)
c_bytesize.bs_size_add.argtypes = [POINTER(SizeStruct), POINTER(SizeStruct)]
c_bytesize.bs_size_grow.restype = POINTER(SizeStruct)
c_bytesize.bs_size_grow.argtypes = [POINTER(SizeStruct), POINTER(SizeStruct)]
c_bytesize.bs_size_add_bytes.restype = POINTER(SizeStruct)
c_bytesize.bs_size_add_bytes.argtypes = [POINTER(SizeStruct), ctypes.c_ulonglong]
c_bytesize.bs_size_grow_bytes.restype = POINTER(SizeStruct)
c_bytesize.bs_size_grow_bytes.argtypes = [POINTER(SizeStruct), ctypes.c_ulonglong]
c_bytesize.bs_size_sub.restype = POINTER(SizeStruct)
c_bytesize.bs_size_sub.argtypes = [POINTER(SizeStruct), POINTER(SizeStruct)]
c_bytesize.bs_size_shrink.restype = POINTER(SizeStruct)
c_bytesize.bs_size_shrink.argtypes = [POINTER(SizeStruct), POINTER(SizeStruct)]
c_bytesize.bs_size_sub_bytes.restype = POINTER(SizeStruct)
c_bytesize.bs_size_sub_bytes.argtypes = [POINTER(SizeStruct), ctypes.c_ulonglong]
c_bytesize.bs_size_shrink_bytes.restype = POINTER(SizeStruct)
c_bytesize.bs_size_shrink_bytes.argtypes = [POINTER(SizeStruct), ctypes.c_ulonglong]
c_bytesize.bs_size_mul_int.restype = POINTER(SizeStruct)
c_bytesize.bs_size_mul_int.argtypes = [POINTER(SizeStruct), ctypes.c_ulonglong]
c_bytesize.bs_size_grow_mul_int.restype = POINTER(SizeStruct)
c_bytesize.bs_size_grow_mul_int.argtypes = [POINTER(SizeStruct), ctypes.c_ulonglong]
c_bytesize.bs_size_mul_float_str.restype = POINTER(SizeStruct)
c_bytesize.bs_size_mul_float_str.argtypes = [POINTER(SizeStruct), ctypes.c_char_p, POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_grow_mul_float_str.restype = POINTER(SizeStruct)
c_bytesize.bs_size_grow_mul_float_str.argtypes = [POINTER(SizeStruct), ctypes.c_char_p, POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_div.restype = ctypes.c_ulonglong
c_bytesize.bs_size_div.argtypes = [POINTER(SizeStruct), POINTER(SizeStruct), POINTER(ctypes.c_int), POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_div_int.restype = POINTER(SizeStruct)
c_bytesize.bs_size_div_int.argtypes = [POINTER(SizeStruct), ctypes.c_ulonglong, POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_shrink_div_int.restype = POINTER(SizeStruct)
c_bytesize.bs_size_shrink_div_int.argtypes = [POINTER(SizeStruct), ctypes.c_ulonglong, POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_true_div.restype = ctypes.c_char_p
c_bytesize.bs_size_true_div.argtypes = [POINTER(SizeStruct), POINTER(SizeStruct), POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_true_div_int.restype = ctypes.c_char_p
c_bytesize.bs_size_true_div_int.argtypes = [POINTER(SizeStruct), ctypes.c_ulonglong, POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_mod.restype = POINTER(SizeStruct)
c_bytesize.bs_size_mod.argtypes = [POINTER(SizeStruct), POINTER(SizeStruct), POINTER(POINTER(SizeErrorStruct))]
c_bytesize.bs_size_round_to_nearest.restype = POINTER(SizeStruct)
c_bytesize.bs_size_round_to_nearest.argtypes = [POINTER(SizeStruct), POINTER(SizeStruct), ctypes.c_int, POINTER(POINTER(SizeErrorStruct))]

## Comparisons
c_bytesize.bs_size_cmp.restype = ctypes.c_int
c_bytesize.bs_size_cmp.argtypes = [POINTER(SizeStruct), POINTER(SizeStruct), ctypes.c_bool]
c_bytesize.bs_size_cmp_bytes.restype = ctypes.c_int
c_bytesize.bs_size_cmp_bytes.argtypes = [POINTER(SizeStruct), ctypes.c_ulonglong, ctypes.c_bool]


def _str_to_decimal(num_str):
    radix = locale.nl_langinfo(locale.RADIXCHAR)
    if radix != '.':
        num_str = num_str.replace(radix, '.')

    return Decimal(num_str)

def neutralize_none_operand(fn):
    def fn_with_neutralization(sz, other):
        return fn(sz, Size(0) if other is None else other)
    return fn_with_neutralization

class Size(object):
    def __init__(self, spec=None):
        self._c_size = None
        try:
            if isinstance(spec, six.string_types):
                self._c_size = SizeStruct.new_from_str(spec)
            elif isinstance(spec, six.integer_types):
                abs_val = abs(spec)
                if abs_val == spec:
                    sgn = 1
                else:
                    sgn = -1
                if abs_val <= MAXUINT64:
                    self._c_size = SizeStruct.new_from_bytes(abs_val, sgn)
                else:
                    self._c_size = SizeStruct.new_from_str(str(spec))
            elif isinstance(spec, (Decimal, float)):
                self._c_size = SizeStruct.new_from_str(str(spec))
            elif isinstance(spec, SizeStruct):
                self._c_size = SizeStruct.new_from_size(spec)
            elif isinstance(spec, Size):
                self._c_size = SizeStruct.new_from_size(spec._c_size)
            elif spec is None:
                self._c_size = SizeStruct.new()
            else:
                raise ValueError("Cannot construct new size from '%s'" % spec)
        except SizeError as e:
            raise ValueError(e)


    ## METHODS ##
    def get_bytes(self):
        try:
            val, sgn = self._c_size.get_bytes()
            return val * sgn
        except SizeError:
            return int(self._c_size.get_bytes_str())

    def convert_to(self, unit):
        if isinstance(unit, six.string_types):
            real_unit = unit_strs.get(unit)
            if real_unit is None:
                raise ValueError("Invalid unit specification: '%s'" % unit)
            ret = self._c_size.convert_to(real_unit)
        else:
            ret = self._c_size.convert_to(unit)

        return _str_to_decimal(ret)

    def human_readable(self, min_unit=B, max_places=2, xlate=True):
        if isinstance(min_unit, six.string_types):
            if min_unit in unit_strs.keys():
                min_unit = unit_strs[min_unit]
            else:
                raise ValueError("Invalid unit specification: '%s'" % min_unit)
        if not isinstance(max_places, six.integer_types):
            raise ValueError("max_places has to be an integer number")
        return self._c_size.human_readable(min_unit, max_places, xlate)

    def round_to_nearest(self, round_to, rounding):
        if isinstance(round_to, Size):
            return Size(self._c_size.round_to_nearest(round_to._c_size, rounding))

        size = None
        # else try to create a SizeStruct instance from it
        for (unit_str, unit) in unit_strs.items():
            if round_to in (unit.real, unit_str):
                size = SizeStruct.new_from_str("1 %s" % unit_str)
                break
        if size is not None:
            return Size(self._c_size.round_to_nearest(size, rounding))
        else:
            raise ValueError("Invalid size specification: '%s'"  % round_to)

    def cmp(self, other, abs_vals=False):
        if isinstance(other, six.integer_types):
            if (other < 0 and abs_vals):
                other = abs(other)
            if 0 <= other <= MAXUINT64:
                return self._c_size.cmp_bytes(other, abs_vals)
            else:
                other = SizeStruct.new_from_str(str(other))
        elif isinstance(other, (Decimal, float)):
            other = SizeStruct.new_from_str(str(other))
        elif isinstance(other, Size):
            other = other._c_size
        elif other is None:
            return 1

        return self._c_size.cmp(other, abs_vals)


    ## INTERNAL METHODS ##
    def __eq__(self, other):
        return self.cmp(other, False) == 0

    def __ne__(self, other):
        return self.cmp(other, False) != 0

    def __lt__(self, other):
        return self.cmp(other, False) == -1

    def __le__(self, other):
        return self.cmp(other, False) in (-1, 0)

    def __gt__(self, other):
        return self.cmp(other, False) == 1

    def __ge__(self, other):
        return self.cmp(other, False) in (1, 0)

    def __bool__(self):
        return self.get_bytes() != 0

    __nonzero__ = __bool__

    def __abs__(self):
        return Size(abs(self.get_bytes()))

    def __neg__(self):
        return self.__mul__(-1)

    @neutralize_none_operand
    def __add__(self, other):
        if isinstance(other, six.integer_types):
            if other <= MAXUINT64:
                return Size(self._c_size.add_bytes(other))
            else:
                other = SizeStruct.new_from_str(str(other))
        elif isinstance(other, (Decimal, float)):
            other = SizeStruct.new_from_str(str(other))
        elif isinstance(other, Size):
            other = other._c_size
        return Size(self._c_size.add(other))

    # needed to make sum() work with Size arguments
    __radd__ = __add__

    @neutralize_none_operand
    def __sub__(self, other):
        if isinstance(other, six.integer_types):
            if other <= MAXUINT64:
                return Size(self._c_size.sub_bytes(other))
            else:
                other = SizeStruct.new_from_str(str(other))
        elif isinstance(other, (Decimal, float)):
            other = SizeStruct.new_from_str(str(other))
        elif isinstance(other, Size):
            other = other._c_size
        return Size(self._c_size.sub(other))

    @neutralize_none_operand
    def __rsub__(self, other):
        other = SizeStruct.new_from_str(str(other))
        return Size(SizeStruct.sub(other, self._c_size))

    @neutralize_none_operand
    def __mul__(self, other):
        if isinstance(other, (Size, SizeStruct)):
            raise ValueError("Cannot multiply Size by Size. It just doesn't make sense.")
        elif isinstance(other, (Decimal, float)) or (isinstance(other, six.integer_types)
                                                     and other > MAXUINT64 or other < 0):
            return Size(self._c_size.mul_float_str(str(other)))
        else:
            return Size(self._c_size.mul_int(other))

    __rmul__ = __mul__

    @neutralize_none_operand
    def __div__(self, other):
        if not six.PY2:
            raise AttributeError

        if isinstance(other, six.integer_types):
            if other <= MAXUINT64:
                return Size(self._c_size.div_int(other))
            else:
                other = SizeStruct.new_from_str(str(other))
                return Size(_str_to_decimal(self._c_size.true_div(other)))
        elif isinstance(other, (Decimal, float)):
            other = SizeStruct.new_from_str(str(other))
            return Size(self._c_size.true_div(other))
        else:
            return _str_to_decimal(self._c_size.true_div(other._c_size))

    @neutralize_none_operand
    def __truediv__(self, other):
        if isinstance(other, six.integer_types):
            if other <= MAXUINT64:
                return Size(self._c_size.true_div_int(other))
            else:
                other = SizeStruct.new_from_str(str(other))
                return Size(self._c_size.true_div(other))
        elif isinstance(other, (Decimal, float)):
            return Size(self._c_size.mul_float_str(str(Decimal(1)/Decimal(other))))

        return _str_to_decimal(self._c_size.true_div(other._c_size))

    def _safe_floordiv(self, other):
        try:
            val, sgn = self._c_size.div(other._c_size)
            return val * sgn
        except OverflowError:
            return int(float(self._c_size.true_div(other._c_size)))

    def _safe_floordiv_int(self, other):
        try:
            return Size(self._c_size.div_int(other))
        except OverflowError:
            return Size(float(self._c_size.true_div_int(other)))

    @neutralize_none_operand
    def __floordiv__(self, other):
        if isinstance(other, (Decimal, float)):
            return Size(self._c_size.mul_float_str(str(Decimal(1)/Decimal(other))))
        elif isinstance(other, six.integer_types):
            if other <= MAXUINT64:
                return self._safe_floordiv_int(other)
            else:
                other = SizeStruct.new_from_str(str(other))
                return Size(self._safe_floordiv(other))
        return self._safe_floordiv(other)

    @neutralize_none_operand
    def __mod__(self, other):
        if not isinstance(other, Size):
            raise ValueError("modulo operation only supported between two Size instances")
        return Size(self._c_size.mod(other._c_size))

    @neutralize_none_operand
    def __divmod__(self, other):
        rdiv = self.__floordiv__(other)
        if not isinstance(other, Size):
            rmod = self.__mod__(rdiv)
        else:
            rmod = self.__mod__(other)

        return (rdiv, rmod)

    def __repr__(self):
        return "Size (%s)" % self.human_readable(B, -1, False)

    def __str__(self):
        return self.human_readable()

    def __int__(self):
        return self.get_bytes()

    def __float__(self):
        return float(self.get_bytes())

    def __deepcopy__(self, memo_dict):
        return Size(self)

    # pickling support for Size
    # see https://docs.python.org/3/library/pickle.html#object.__reduce__
    def __reduce__(self):
        return (self.__class__, (self.get_bytes(),))

    def __hash__(self):
        return self.get_bytes()
