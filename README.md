### CI status

<img alt="CI status" src="https://fedorapeople.org/groups/storage_apis/statuses/libbytesize-master.svg" width="100%" height="275ex" />


### Introduction

The goal of this project is to provide a tiny library that would facilitate the
common operations with sizes in bytes. Many projects need to work with sizes in
bytes (be it sizes of storage space, memory,...) and all of them need to deal
with the same issues like:

* How to get a human-readable string for the given size?
* How to store the given size so that no significant information is lost?
* If we store the size in bytes, what if the given size gets over the ``MAXUINT64``
  value?
* How to interpret sizes entered by users according to their locale and typing
  conventions?
* How to deal with the decimal/binary units (*MB* vs. *MiB*) ambiguity?

Some projects have all the above questions/concerns addressed well, some have
them addressed partially some simply don't care. However, having (partial)
solutions implemented in multiple places every time with a different set of
bugs, differences in behaviour and this or that missing is a waste of time and
effort. We need a generally usable solution that could be used by every project
that needs to deal with sizes in bytes.

Since the goal is to provide a solution as much generally usable as possible the
implementation has to be small, fast and written in a language that can be
easily interfaced from other languages. The current obvious choice is the *C*
language with thin bindings for other languages.
