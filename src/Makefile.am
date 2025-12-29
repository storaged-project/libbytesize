AM_CPPFLAGS = -DLOCALEDIR=\"$(localedir)\" -DDEFAULT_TEXT_DOMAIN=\"libbytesize\"
LDADD = $(LIBINTL)

lib_LTLIBRARIES = libbytesize.la
libbytesize_la_CFLAGS = -Wall -Wextra -Werror -Wno-overflow -D_GNU_SOURCE
libbytesize_la_LIBADD = -lgmp $(PCRE2_LIBS)
libbytesize_la_LDFLAGS = -version-info 1:0:0
libbytesize_la_SOURCES = bs_size.c bs_size.h gettext.h

noinst_dist_SOURCES = gettext.h

libincludedir = $(includedir)/bytesize
libinclude_HEADERS = bs_size.h

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = ${builddir}/bytesize.pc

SUBDIRS = python
MAINTAINERCLEANFILES = Makefile.in bytesize.pc
