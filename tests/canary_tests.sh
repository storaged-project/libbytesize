#!/bin/sh -e
# Run the translation canary tests on the translatable strings

# If not run from automake, fake it
if [ -z "$top_srcdir" ]; then
    top_srcdir="$(dirname "$0")/.."
fi

if [ -z "$top_builddir" ] ; then
    top_builddir="$(dirname "$0")/.."
fi

# Make sure libbytesize.pot is up to date
make -C ${top_builddir}/po libbytesize.pot-update >/dev/null 2>&1

PYTHONPATH="${PYTHONPATH}:${top_srcdir}/translation-canary"
export PYTHONPATH

# Run the translatable tests on the POT file
python3 -m translation_canary.translatable "${top_srcdir}/po/libbytesize.pot"
