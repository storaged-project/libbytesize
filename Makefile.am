ACLOCAL_AMFLAGS = -I m4
DISTCHECK_CONFIGURE_FLAGS = --enable-introspection

SUBDIRS = . po src dist tests
if WITH_GTK_DOC
SUBDIRS += docs
endif
if WITH_TOOLS
SUBDIRS += tools
endif

dist_noinst_DATA = LICENSE README.md

MAINTAINERCLEANFILES = Makefile.in aclocal.m4 config.guess config.sub \
    configure depcomp install-sh ltmain.sh missing py-compile compile ar-lib \
    m4/*.m4

LIBDIRS = src/.libs
PYTHONDIR = src/python

TEST_PYTHON ?= $(PYTHON)

ZANATA_PULL_ARGS = --transdir ./po/
ZANATA_PUSH_ARGS = --srcdir ./po/ --push-type source --force

TEST_DEPENDENCIES = $(shell rpm --specfile dist/libbytesize.spec --requires | cut -d' ' -f1 | grep -v ^libbytesize)
TEST_DEPENDENCIES += gmp gmp-devel
TEST_DEPENDENCIES += mpfr mpfr-devel
TEST_DEPENDENCIES += pcre2 pcre2-devel

# If translations are present, run tests on the .po files before tarring them
# up to remove any .po files with errors. Use a weird looking loop since shell
# doesn't have a good way to test for a wildcard.
dist-hook:
	for p in $(distdir)/po/*.po ; do \
	    if [ -e "$$p" ]; then \
		PYTHONPATH=$(srcdir)/translation-canary python3 -m translation_canary.translated \
		    --release $(distdir)/po ; \
	    fi ; \
	    break ; \
	done

run-ipython: all
	LD_LIBRARY_PATH=${LIBDIRS} PYTHONPATH=$(PYTHONDIR) ipython3

check-requires:
	@echo "*** Checking if the dependencies required for testing and analysis are available ***"
	@status=0 ; \
	for pkg in $(TEST_DEPENDENCIES) ; do \
		test_output="$$(rpm -q --whatprovides "$$pkg")" ; \
		if [ $$? != 0 ]; then \
			echo "$$test_output" ; \
			status=1 ; \
		fi ; \
	done ; \
	exit $$status

install-requires:
	@echo "*** Installing the dependencies required for testing and analysis ***"
	dnf install -y $(TEST_DEPENDENCIES)

test:
	$(MAKE) check

ci:
	$(MAKE) distcheck; \
	status="$$?" ; \
	find . -name 'test-suite.log' -exec cat '{}' \; ; \
	test "$$status" = "0"

po-pull:
	@which zanata >/dev/null 2>&1 || ( echo "You need to install Zanata client to download translation files"; exit 1 )
	zanata pull $(ZANATA_PULL_ARGS)

tag:
	@TAG="$(PACKAGE_VERSION)" ; \
	git tag -a -s -m "Tag as $$TAG" -f "$$TAG" && \
	echo "Tagged as $$TAG"

rpmlog:
	@cl=`grep -n %changelog dist/libbytesize.spec.in |cut -d : -f 1` ; \
	version_release=`tail --lines=+$$(($$cl + 1)) dist/libbytesize.spec.in|head -1|cut -d- -f2-3|sed 's/ //g'|sed -r 's/-[0-9]+//'` ; \
	git log --no-merges --pretty="format:- %s (%ae)" "$$version_release.." |sed -e 's/@.*)/)/' ; \
	echo

shortlog:
	git shortlog -r --no-merges --format="- %s" -w76,0,2 $$(git tag -l | grep '^[0-9]' | tail -n 1)..HEAD | sed 's/"):$"/"):\n"/g'

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

archive: po-pull
	$(MAKE) distcheck

local: all
	[ -f ./po/en_US.po ] || msginit -i ./po/$(PACKAGE_NAME).pot -o ./po/en_US.po --no-translator
	$(MAKE) dist

srpm: local
	rpmbuild -ts --nodeps $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz
	rm -f $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz

rpm: local
	rpmbuild -tb --nodeps $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz
	rm -f $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz

release: tag
	$(MAKE) archive
	$(MAKE) -C po/ $(PACKAGE_NAME).pot-update
	zanata push $(ZANATA_PUSH_ARGS)

EXTRA_DIST = config.rpath

# Include the xgettext wrapper so pot-update can be run from the source distribution
# This is needed for make distcheck.
EXTRA_DIST += $(srcdir)/translation-canary/xgettext_werror.sh
