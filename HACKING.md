CODING STYLE
============

 - Please follow the coding style already used.

 - Spaces, not tabs, are used (except for Makefiles).


MAKING RELEASES
===============

 - [ ] ``sudo git clean -xdf``

 - [ ] ``./autogen.sh && ./configure``

 - [ ] ``make bumpver``

 - [ ] Add a new entry to the *NEWS.rst* file (full list of changes should be
       generated with ``make shortlog``).

 - [ ] Regenerate the bscalc.man manpage by installing bscalc and then running
       ``help2man -N bscalc > PATH_TO_LIBBYTESIZE/tools/bscalc.man``.

 - [ ] Commit all the changes as *New version - $VERSION*.

 - [ ] ``make release`` (requires a GPG key to sign the tag)

 - [ ] ``git push && git push --tags``

 - [ ] Edit the new release (for the new tag) at GitHub and:

   - [ ] add some detailed information about it (from the *NEWS.rst*) file to it,

   - [ ] upload the tarball created above (``make release``) to the release.

 - [ ] Update the documentation by copying the contents of the *docs/html*
       folder to the *libbytesize* directory in the
       [Storaged project website repository](https://github.com/storaged-project/storaged-project.github.io)
       and commit and push the changes
