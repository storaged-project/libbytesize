#!/usr/bin/python3

import sys
from argparse import ArgumentParser
from decimal import Decimal, InvalidOperation
from bytesize import Size, ZeroDivisionError

b_units = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB")
d_units = ("KB", "MB", "GB", "TB", "PB", "EB")

_WHITESPACE = {" ", "\t", "\n"}
_OPERATORS = {"+", "-", "*", "/", "%", "(", ")"}  # TODO: add divmod
_DOUBLE_OPERATORS = {"/", "*"}  # // and ** are valid operators too
_EXP_OPERATORS = {"-", "+"}     # 1e+2, 1e-2

def _get_operand(op_str):
    try:
        return int(op_str)
    except ValueError:
        try:
            return Decimal(op_str)
        except InvalidOperation:
            return Size(op_str)


def _tokenize(expression):
    tokens = []
    operand_str_start = -1
    for i, char in enumerate(expression):
        if char in _WHITESPACE:
            continue
        elif char in _OPERATORS:
            if char in _EXP_OPERATORS and expression[i - 1] in ("e", "E"):
                continue
            if char in _DOUBLE_OPERATORS and expression[i - 1] == char:
                # see _DOUBLE_OPERATORS above
                tokens[-1] = tokens[-1] + char
                continue
            if operand_str_start != -1:
                op = _get_operand(expression[operand_str_start:i])
                tokens.append(op)
                operand_str_start = -1
            tokens.append(expression[i])
        elif operand_str_start == -1:
            operand_str_start = i
    if operand_str_start != -1:
        op = _get_operand(expression[operand_str_start:])
        tokens.append(op)
    return tokens


def _tokens_to_eval_str(tokens):
    eval_tokens = []
    for token in tokens:
        if isinstance(token, int):
            eval_tokens.append("%d" % token)
        elif isinstance(token, Decimal):
            eval_tokens.append("Decimal('%s')" % token)
        elif isinstance(token, Size):
            eval_tokens.append("Size(%d)" % token)
        else:
            eval_tokens.append(token)

    return " ".join(eval_tokens)


def _print_result(result, args):
    # TODO: support configurable n_places (aligned printing is not so easy then)
    n_places = 2
    if isinstance(result, Size):
        if args.unit is not None:
            value = result.convert_to(args.unit)
            if int(value) == value:
                print("%d %s" % (int(value), args.unit))
            else:
                print(("%0." + str(n_places) + "f" + " %s") % (value, args.unit))
        else:
            in_bytes = "%d B" % int(result)
            print(in_bytes)

            format_str = "%" + str(len(in_bytes) - n_places) + "." + str(n_places) + "f"
            for b_unit in b_units[1:]:
                converted = (format_str % result.convert_to(b_unit))
                # don't print "0.00 CRAZY_BIG_UNIT"
                if converted.strip() not in ("0." + n_places * "0", "-0." + n_places * "0"):
                    print("%s %s" % (converted, b_unit))
    else:
        print(str(result))


def _main():
    ap = ArgumentParser(epilog="Report issues at https://github.com/storaged-project/libbytesize/issues")
    ap.add_argument("-u", "--unit", choices=(b_units + d_units),
                    help="Unit to show the result in")
    ap.add_argument("-b", "-B", dest="unit", const="B",
                    help="Show result in bytes", action="store_const")
    for b_unit in b_units[1:]:
        ap.add_argument("-" + b_unit[0].lower(), "-" + b_unit[0], "--" + b_unit,
                        dest="unit", const=b_unit,
                        help="Show result in " + b_unit, action="store_const")
    for d_unit in d_units:
        ap.add_argument("--" + d_unit,
                        dest="unit", const=d_unit,
                        help="Show result in " + d_unit, action="store_const")
    ap.add_argument(metavar="EXPRESSION_PART", dest="expressions", nargs="+")

    args = ap.parse_args()

    try:
        tokens = _tokenize(" ".join(args.expressions))
    except ValueError as e:
        print("Error while parsing expression: %s" % e)
        return 1

    eval_str = _tokens_to_eval_str(tokens)
    try:
        result = eval(eval_str)
    except (TypeError, ValueError, ZeroDivisionError) as e:
        print("Error during evaluation: %s" % e)
        return 1
    except SyntaxError as e:
        print("Error during evaluation: %s" % e.msg)
        print(eval_str)
        print(" " * (e.offset - 1) + "^")
        return 1

    _print_result(result, args)

    return 0


if __name__ == "__main__":
    sys.exit(_main())
