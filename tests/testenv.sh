#!/bin/sh

if [ -z "$top_srcdir" ]; then
    echo "*** top_srcdir must be set"
fi

# If no top_builddir is set, use top_srcdir
: "${top_builddir:=$top_srcdir}"

if [ -z "$PYTHONPATH" ]; then
    PYTHONPATH="${top_srcdir}/src/python"
else
    PYTHONPATH="${PYTHONPATH}:${top_srcdir}/src/python"
fi

if [ -z "$LD_LIBRARY_PATH" ]; then
    LD_LIBRARY_PATH="${top_builddir}/src/.libs"
else
    LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:${top_builddir}/src/.libs"
fi

export PYTHONPATH
export LD_LIBRARY_PATH
export top_srcdir
export top_builddir
