"""
This code wraps the bindings automatically created by gobject-introspection.
They allow for creating more pythonic bindings where necessary. For instance
this code allows many functions with default-value arguments to be called
without specifying values for such arguments. Also the overrides provides some
of the internal methods providing some standard functionality (like __str__ for
conversion to a string, etc.).

The overriden methods also provide a nicer API doing some type conversions
implicitly. E.g. when the original C function returns a floating-point number
represented as a string (because of the possible loss of precision when using
float) the overriden method implicitly converts such string into a Decimal
instance which preserves the precision, but behaves like a number. Also, if
there are multiple functions that only differ in the type of their parameters,
an override is provided such that a type of the parameter is checked and the
proper C function is called then.

"""

import six
from decimal import Decimal

from gi.repository import GLib
from gi.importer import modules
from gi.overrides import override

ByteSize = modules['ByteSize']._introspection_module
__all__ = []

B = ByteSize.Bunit.B
KiB = ByteSize.Bunit.KIB
MiB = ByteSize.Bunit.MIB
GiB = ByteSize.Bunit.GIB
TiB = ByteSize.Bunit.TIB
PiB = ByteSize.Bunit.PIB
EiB = ByteSize.Bunit.EIB
ZiB = ByteSize.Bunit.ZIB
YiB = ByteSize.Bunit.YIB
KB = ByteSize.Dunit.KB
MB = ByteSize.Dunit.MB
GB = ByteSize.Dunit.GB
TB = ByteSize.Dunit.TB
PB = ByteSize.Dunit.PB
EB = ByteSize.Dunit.EB
ZB = ByteSize.Dunit.ZB
YB = ByteSize.Dunit.YB

__all__.extend(("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"))

unit_strs = {
    "B": B, "KiB": KiB, "MiB": MiB, "GiB": GiB, "TiB": TiB, "PiB": PiB, "EiB": EiB, "ZiB": ZiB, "YiB": YiB,
    "KB": KB, "MB": MB, "GB": GB, "TB": TB, "PB": PB, "EB": EB, "ZB": ZB, "YB": YB,
    }

ROUND_UP = ByteSize.RoundDir.UP
ROUND_DOWN = ByteSize.RoundDir.DOWN
__all__.extend(("ROUND_UP", "ROUND_DOWN"))

class Size(ByteSize.Size):
    def __new__(cls, spec=None):
        try:
            if isinstance(spec, six.string_types):
                ret = ByteSize.Size.new_from_str(spec)
            elif isinstance(spec, six.integer_types):
                abs_val = abs(spec)
                if abs_val == spec:
                    sgn = 1
                else:
                    sgn = -1
                if abs_val <= GLib.MAXUINT64:
                    ret = ByteSize.Size.new_from_bytes(abs_val, sgn)
                else:
                    ret = ByteSize.Size.new_from_str(str(spec))
            elif isinstance(spec, (Decimal, float)):
                ret = ByteSize.Size.new_from_str(str(spec))
            elif isinstance(spec, ByteSize.Size):
                ret = ByteSize.Size.new_from_size(spec)
            elif spec is None:
                ret = ByteSize.Size.new()
            else:
                raise ValueError("Cannot construct new size from '%s'" % spec)
        except GLib.Error as e:
            raise ValueError(e.message)

        ret.__class__ = cls
        return ret

    ## METHODS ##
    def get_bytes(self):
        try:
            val, sgn = ByteSize.Size.get_bytes(self)
            return val * sgn
        except GLib.Error:
            return int(ByteSize.Size.get_bytes_str(self))

    def convert_to(self, unit):
        if isinstance(unit, six.string_types):
            real_unit = unit_strs.get(unit)
            if real_unit is None:
                raise ValueError("Invalid unit specification: '%s'" % unit)
            return Decimal(ByteSize.Size.convert_to(self, real_unit))
        else:
            return Decimal(ByteSize.Size.convert_to(self, unit))

    def human_readable(self, min_unit=ByteSize.Bunit.B, max_places=2, xlate=True):
        if isinstance(min_unit, six.string_types):
            if min_unit in unit_strs.keys():
                min_unit = unit_strs[min_unit]
            else:
                raise ValueError("Invalid unit specification: '%s'" % min_unit)
        return ByteSize.Size.human_readable(self, min_unit, max_places, xlate)

    def round_to_nearest(self, round_to, rounding=ByteSize.RoundDir.UP):
        if isinstance(round_to, ByteSize.Size):
            return ByteSize.Size.round_to_nearest(self, round_to, rounding)

        size = None
        # else try to create a ByteSize.Size instance from it
        for (unit_str, unit) in unit_strs.items():
            if round_to in (unit.real, unit_str):
                size = ByteSize.Size.new_from_str("1 %s" % unit_str)
                break
        if size is not None:
            return ByteSize.Size.round_to_nearest(self, size, rounding)
        else:
            raise ValueError("Invalid size specification: '%s'"  % round_to)

    def cmp(self, other, abs_vals=False):
        if isinstance(other, six.integer_types):
            if (other < 0 and abs_vals):
                other = abs(other)
            if other <= GLib.MAXUINT64:
                return ByteSize.Size.cmp_bytes(self, other, abs_vals) == 0
            else:
                other = ByteSize.Size.new_from_str(str(other))
        elif isinstance(other, (Decimal, float)):
            other = ByteSize.Size.new_from_str(str(other))

        return ByteSize.Size.cmp(self, other, abs_vals)


    ## INTERNAL METHODS ##
    def __eq__(self, other):
        return self.cmp(other, False) == 0

    def __ne__(self, other):
        return self.cmp(other, False) != 0

    def __lt__(self, other):
        return self.cmp(other, False) == -1

    def __le__(self, other):
        return self.cmp(other, False) in (-1, 0)

    def __gt__(segf, other):
        return segf.cmp(other, False) == 1

    def __ge__(segf, other):
        return segf.cmp(other, False) in (1, 0)

    def __add__(self, other):
        if isinstance(other, six.integer_types):
            if other <= GLib.MAXUINT64:
                return ByteSize.Size.add_bytes(self, other)
            else:
                other = ByteSize.Size.new_from_str(str(other))
        elif isinstance(other, (Decimal, float)):
            other = ByteSize.Size.new_from_str(str(other))
        return ByteSize.Size.add(self, other)

    # needed to make sum() work with Size arguments
    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, six.integer_types):
            if other <= GLib.MAXUINT64:
                return ByteSize.Size.sub_bytes(self, other)
            else:
                other = ByteSize.Size.new_from_str(str(other))
        elif isinstance(other, (Decimal, float)):
            other = ByteSize.Size.new_from_str(str(other))
        return ByteSize.Size.sub(self, other)

    def __rsub__(self, other):
        other = ByteSize.Size.new_from_str(str(other))
        return ByteSize.Size.sub(other, self)

    def __mul__(self, other):
        if isinstance(other, ByteSize.Size):
            raise ValueError("Cannot multiply Size by Size. It just doesn't make sense.")
        elif isinstance(other, (Decimal, float)) or (isinstance(other, six.integer_types)
                                                     and other > GLib.MAXUINT64):
            return ByteSize.Size.mul_float_str(self, str(other))
        else:
            return ByteSize.Size.mul_int(self, other)

    __rmul__ = __mul__

    def __div__(self, other):
        if not six.PY2:
            raise AttributeError

        if isinstance(other, six.integer_types):
            if other <= GLib.MAXUINT64:
                return ByteSize.Size.div_int(self, other)
            else:
                other = ByteSize.Size.new_from_str(str(other))
                return int(Decimal(ByteSize.Size.true_div(self, other)))
        elif isinstance(other, (Decimal, float)):
            other = ByteSize.Size.new_from_str(str(other))
        else:
            return Decimal(ByteSize.Size.true_div(self, other))

    def __truediv__(self, other):
        if isinstance(other, six.integer_types):
            if other <= GLib.MAXUINT64:
                return Decimal(ByteSize.Size.true_div_int(self, other))
            else:
                other = ByteSize.Size.new_from_str(str(other))
        elif isinstance(other, (Decimal, float)):
            other = ByteSize.Size.new_from_str(str(other))

        return Decimal(ByteSize.Size.true_div(self, other))

    def __floordiv__(self, other):
        if isinstance(other, six.integer_types):
            if other <= GLib.MAXUINT64:
                return ByteSize.Size.div_int(self, other)
            else:
                other = ByteSize.Size.new_from_str(str(other))

        return ByteSize.Size.div(self, other)

    def __mod__(self, other):
        return ByteSize.Size.mod(self, other)

    def __repr__(self):
        return "Size (%s)" % self.human_readable(ByteSize.Bunit.B, -1, False)

    def __str__(self):
        return self.human_readable()

    def __int__(self):
        return self.get_bytes()

    def __float__(self):
        return float(self.get_bytes())

    def __deepcopy__(self):
        return ByteSize.Size.new_from_size(self)

    # pickling support for Size
    # see https://docs.python.org/3/library/pickle.html#object.__reduce__
    def __reduce__(self):
        return (self.__class__, (self.get_bytes(),))

Size = override(Size)
__all__.append("Size")
