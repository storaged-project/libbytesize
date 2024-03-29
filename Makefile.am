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

install-requires:
	@echo "*** Installing the dependencies required for testing and analysis ***"
	@which ansible-playbook >/dev/null 2>&1 || ( echo "Please install Ansible to install testing dependencies"; exit 1 )
	@ansible-playbook -K -i "localhost," -c local misc/install-test-dependencies.yml

pylint:
	@echo "*** Running pylint ***"
	@python3 -m pylint --version >/dev/null 2>&1; \
	if test $$? != 0 ; then \
		echo "pylint not available, skipping" ; \
	fi

	PYTHONPATH=src/python:$(PYTHONPATH) $(PYTHON) -m pylint -E tools/bs_calc.py.in

pep8:
	@echo "*** Running pep8 compliance check ***"
	@if test `which pycodestyle-3` ; then \
		pep8='pycodestyle-3' ; \
	elif test `which pycodestyle` ; then \
		pep8='pycodestyle' ; \
	elif test `which pep8` ; then \
		pep8='pep8' ; \
	else \
		echo "You need to install pycodestyle/pep8 to run this check."; exit 1; \
	fi ; \
	$$pep8 --ignore=E501,E402,E731,W504 tools/bs_calc.py.in


test:
	@status=0; \
	$(MAKE) check || status=1; \
	$(MAKE) pep8 || status=1; \
	$(MAKE) pylint || status=1; \
	exit $$status

ci:
	$(MAKE) distcheck; \
	status="$$?" ; \
	find . -name 'test-suite.log' -exec cat '{}' \; ; \
	test "$$status" = "0"

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
	$(MAKE) -C po/ $(PACKAGE_NAME).pot-update

archive:
	$(MAKE) distcheck

local: all
	$(MAKE) dist

srpm: local
	rpmbuild -ts --nodeps $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz
	rm -f $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz

rpm: local
	rpmbuild -tb --nodeps $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz
	rm -f $(PACKAGE_NAME)-$(PACKAGE_VERSION).tar.gz

release: tag
	$(MAKE) archive

EXTRA_DIST = config.rpath

# Include the xgettext wrapper so pot-update can be run from the source distribution
# This is needed for make distcheck.
EXTRA_DIST += $(srcdir)/translation-canary/xgettext_werror.sh
