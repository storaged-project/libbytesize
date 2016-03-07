ACLOCAL_AMFLAGS = -I m4
DISTCHECK_CONFIGURE_FLAGS = --enable-introspection

SUBDIRS = po src dist docs tests

dist_noinst_DATA = LICENSE README.rst

MAINTAINERCLEANFILES = Makefile.in aclocal.m4 config.guess config.sub \
    configure depcomp install-sh ltmain.sh missing py-compile compile ar-lib \
    m4/*.m4

LIBDIRS = src/.libs
PYTHONDIR = src/python

TEST_PYTHON ?= $(PYTHON)

run-ipython: all
	LD_LIBRARY_PATH=${LIBDIRS} PYTHONPATH=$(PYTHONDIR) ipython

test: all
	LD_LIBRARY_PATH=${LIBDIRS} PYTHONPATH=$(PYTHONDIR) $(TEST_PYTHON) tests/libbytesize_unittest.py
	LD_LIBRARY_PATH=${LIBDIRS} PYTHONPATH=$(PYTHONDIR) $(TEST_PYTHON) tests/lbs_py_override_unittest.py

ci: distcheck
	TEST_PYTHON=python2 $(MAKE) test
	TEST_PYTHON=python3 $(MAKE) test

tag:
	@TAG="$(PACKAGE_NAME)-$(PACKAGE_VERSION)" ; \
	git tag -a -s -m "Tag as $$TAG" -f "$$TAG" ; \
	echo "Tagged as $$TAG"

rpmlog:
	@cl=`grep -n %changelog dist/libbytesize.spec.in |cut -d : -f 1` ; \
	version_release=`tail --lines=+$$(($$cl + 1)) dist/libbytesize.spec.in|head -1|cut -d- -f2-3|sed 's/ //g'|sed -r 's/-[0-9]+//'` ; \
	git log --pretty="format:- %s (%ae)" "$(PACKAGE_NAME)-$$version_release.." |sed -e 's/@.*)/)/' ; \
	echo

bumpver:
	@VERSION=`echo $(PACKAGE_VERSION)|sed -r 's/(.*)\.([0-9]+)/\1/'` ; \
	SUBVERSION=`echo $(PACKAGE_VERSION)|sed -r 's/.*\.([0-9]+)/\1/'` ; \
	NEWSUBVERSION=$$(($$SUBVERSION + 1)) ; \
	DATELINE="* `date "+%a %b %d %Y"` `git config user.name` <`git config user.email`> - $$VERSION.$$NEWSUBVERSION-1"  ; \
	cl=`grep -n %changelog dist/libbytesize.spec.in |cut -d : -f 1` ; \
	tail --lines=+$$(($$cl + 1)) dist/libbytesize.spec.in > speclog ; \
	(head -n $$cl dist/libbytesize.spec ; echo "$$DATELINE" ; make --quiet rpmlog 2>/dev/null ; echo ""; cat speclog) > dist/libbytesize.spec.in.new ; \
	mv dist/libbytesize.spec.in.new dist/libbytesize.spec.in ; rm -f speclog ; \
	sed -ri "s/(AC_INIT\(\[$(PACKAGE_NAME)\], \[)[0-9]+\.[0-9]+(\],.*)/\1$$VERSION.$$NEWSUBVERSION\2/" configure.ac ; \
	sed -ri "s/Version:(\\s+)[-0-9.]+/Version:\\1$$VERSION.$$NEWSUBVERSION/" dist/libbytesize.spec.in ;

archive: distcheck

local: dist

srpm: local
	rpmbuild -ts --nodeps $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz
	rm -f $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz

rpm: local
	rpmbuild -tb --nodeps $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz
	rm -f $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz

release: tag
	$(MAKE) archive

EXTRA_DIST = config.rpath
