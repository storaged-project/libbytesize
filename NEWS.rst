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