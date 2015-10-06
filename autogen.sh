#!/bin/bash -e
[ -d m4 ] || mkdir m4
autopoint --force
libtoolize --copy --force
aclocal -I m4
autoconf
automake --foreign --add-missing --copy
rm -rf autom4te.cache
