ACLOCAL_AMFLAGS = -I m4
DISTCHECK_CONFIGURE_FLAGS = --enable-introspection

SUBDIRS = . po src dist docs tests

dist_noinst_DATA = LICENSE README.rst

MAINTAINERCLEANFILES = Makefile.in aclocal.m4 config.guess config.sub \
    configure depcomp install-sh ltmain.sh missing py-compile compile ar-lib \
    m4/*.m4

LIBDIRS = src/.libs
PYTHONDIR = src/python

TEST_PYTHON ?= $(PYTHON)

ZANATA_PULL_ARGS = --transdir ./po/
ZANATA_PUSH_ARGS = --srcdir ./po/ --push-type source --force

all-local: po-empty

run-ipython: all
	LD_LIBRARY_PATH=${LIBDIRS} PYTHONPATH=$(PYTHONDIR) ipython

test: check
check: all
	-git checkout HEAD po/libbytesize.pot

ci:
	$(MAKE) distcheck; \
	status="$$?" ; \
	find . -name 'test-suite.log' -exec cat '{}' \; ; \
	test "$$status" = "0"

po-empty:
	for lingua in $$(cat po/LINGUAS) ; do \
		[ -f ./po/$$lingua.po ] || \
		msginit -i ./po/$(PACKAGE_NAME).pot -o ./po/$$lingua.po --no-translator || \
		exit 1 ; \
	done

# After pulling from zanata, use translation-canary to delete any bad
# translations, and then run po-empty to replace them with empty .po files
po-pull:
	rpm -q zanata-python-client &>/dev/null || ( echo "need to run: yum install zanata-python-client"; exit 1 )
	zanata pull $(ZANATA_PULL_ARGS)
	PYTHONPATH=$(srcdir)/translation-canary python3 -m translation_canary.translated \
		   --release --no-modify-linguas $(srcdir)
	$(MAKE) po-empty

tag:
	@TAG="$(PACKAGE_NAME)-$(PACKAGE_VERSION)" ; \
	git tag -a -s -m "Tag as $$TAG" -f "$$TAG" ; \
	echo "Tagged as $$TAG"
	@TAG="$(PACKAGE_VERSION)" ; \
	git tag -a -s -m "Tag as $$TAG" -f "$$TAG" ; \
	echo "Tagged as $$TAG"

rpmlog:
	@cl=`grep -n %changelog dist/libbytesize.spec.in |cut -d : -f 1` ; \
	version_release=`tail --lines=+$$(($$cl + 1)) dist/libbytesize.spec.in|head -1|cut -d- -f2-3|sed 's/ //g'|sed -r 's/-[0-9]+//'` ; \
	git log --no-merges --pretty="format:- %s (%ae)" "$(PACKAGE_NAME)-$$version_release.." |sed -e 's/@.*)/)/' ; \
	echo

bumpver:
	@VERSION=`echo $(PACKAGE_VERSION)|sed -r 's/(.*)\.([0-9]+)/\1/'` ; \
	SUBVERSION=`echo $(PACKAGE_VERSION)|sed -r 's/.*\.([0-9]+)/\1/'` ; \
	NEWSUBVERSION=$$(($$SUBVERSION + 1)) ; \
	DATELINE="* `date "+%a %b %d %Y"` `git config user.name` <`git config user.email`> - $$VERSION.$$NEWSUBVERSION-1"  ; \
	cl=`grep -n %changelog dist/libbytesize.spec.in |cut -d : -f 1` ; \
	tail --lines=+$$(($$cl + 1)) dist/libbytesize.spec.in > speclog ; \
	(head -n $$cl dist/libbytesize.spec.in ; echo "$$DATELINE" ; make --quiet rpmlog 2>/dev/null ; echo ""; cat speclog) > dist/libbytesize.spec.in.new ; \
	mv dist/libbytesize.spec.in.new dist/libbytesize.spec.in ; rm -f speclog ; \
	sed -ri "s/(AC_INIT\(\[$(PACKAGE_NAME)\], \[)[0-9]+\.[0-9]+(\],.*)/\1$$VERSION.$$NEWSUBVERSION\2/" configure.ac ; \
	sed -ri "s/Version:(\\s+)[-0-9.]+/Version:\\1$$VERSION.$$NEWSUBVERSION/" dist/libbytesize.spec.in ;
	$(MAKE) -C po/ $(PACKAGE_NAME).pot-update

archive: po-pull
	$(MAKE) distcheck

local: po-empty
	$(MAKE) dist

srpm: local
	rpmbuild -ts --nodeps $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz
	rm -f $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz

rpm: local
	rpmbuild -tb --nodeps $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz
	rm -f $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz

release: tag
	$(MAKE) archive
	zanata push $(ZANATA_PUSH_ARGS)

EXTRA_DIST = config.rpath

# Include the xgettext wrapper so pot-update can be run from the source distribution
# This is needed for make distcheck.
EXTRA_DIST += $(srcdir)/translation-canary/xgettext_werror.sh
