ACLOCAL_AMFLAGS = -I m4
DISTCHECK_CONFIGURE_FLAGS = --enable-introspection

SUBDIRS = po src dist docs tests

dist_noinst_DATA = LICENSE README.rst

MAINTAINERCLEANFILES = Makefile.in aclocal.m4 config.guess config.sub \
    configure depcomp install-sh ltmain.sh missing py-compile compile ar-lib \
    m4/*.m4

LIBDIRS = src/.libs
GIDIR = src/

TEST_PYTHON ?= $(PYTHON)

run-ipython: all
	PYTHONPATH=src/python GI_TYPELIB_PATH=${GIDIR} LD_LIBRARY_PATH=${LIBDIRS} G_MESSAGES_DEBUG=all ipython

test: all
	GI_TYPELIB_PATH=${GIDIR} LD_LIBRARY_PATH=${LIBDIRS} G_MESSAGES_DEBUG=all $(TEST_PYTHON) tests/libbytesize_unittest.py

ci: distcheck
	TEST_PYTHON=python2 $(MAKE) test
	TEST_PYTHON=python3 $(MAKE) test

EXTRA_DIST = config.rpath
