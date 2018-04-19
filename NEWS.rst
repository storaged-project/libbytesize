Libbytesize 1.3
---------------

New minor release of the libbytesize library. There are only small changes in
this release. Most notable change is new configure option `--without-python2`
that allows building libbytesize without Python 2 support.


**Full list of changes**

Vojtech Trefny (5):

- Do not segfault when trying to bs_size_free NULL
- Fix links for documentation and GH project
- Add gcc to BuildRequires
- Sync spec with downstream
- Allow building libbytesize without Python 2 support

Vratislav Podzimek (1):

- Add a HACKING.rst file

Thanks to all our contributors.

Vojtech Trefny, 2018-04-19

Libbytesize 1.2
---------------

New minor release of the libbytesize library. There are only small changes in
this release.


**Full list of changes**

Vratislav Podzimek (4):

- Do not lie about tag creation
- Do not require the glib-2.0 pkgconfig package
- Use only version as a tag of the last release

Thanks to all our contributors.

Vratislav Podzimek, 2017-09-29


Libbytesize 1.1
---------------

New minor release of the libbytesize library. There are only small changes in
this release and one important bug fix.

**Notable changes**

- Fixed parsing size strings with translated units (e.g. "10 Gio" in French).


**Full list of changes**

Vojtech Trefny (3):

- Use only one git tag for new releases
- Fix source and url in spec file
- Add NEWS.rst file

Vratislav Podzimek (4):

- Add two temporary test files to .gitignore
- Actually translate the units when expected
- Fix the shortlog target
- Sync spec with downstream

Thanks to all our contributors.

Vratislav Podzimek, 2017-09-21


Libbytesize 1.0
---------------

New major release of the libbytesize library. There are only small changes in
this release, mostly bug fixes. The version bump is intended as a statement of
"finishing" work on this library. The API is now stable and we don't plan to
change it or add new major features. Future changes will probably include only
bug fixes.

**Full list of changes**

Vojtech Trefny (1):

- Make more space for CI status image

Vratislav Podzimek (4):

- Properly support 64bit operands
- Remove extra 'is' in two docstrings
- Include limits.h to make sure ULONG_MAX is defined
- New version - 1.0

Thanks to all our contributors.

Vratislav Podzimek, 2017-09-14


Libbytesize 0.11
----------------

New minor release of the libbytesize library. Most changes in this release are
related to fixing new issues and bugs.

**Full list of changes**

Kai Lüke (1):

- Allow non-source directory builds

Vojtech Trefny (7):

- Do not try to run translation tests on CentOS/RHEL 7
- Fix library name in acinclude.m4
- Fix checking for available locales
- Check for requires in generated spec file, not in the template
- Remove "glibc-all-langpacks" from test dependencies
- Fix README file name
- Do not check for test dependencies for every test run

Vratislav Podzimek (4):

- Skip tests if they require unavailable locales
- Add a build status image to the README.md
- Reserve more space for the CI status
- New version - 0.11

Thanks to all our contributors.

Vratislav Podzimek, 2017-06-14
