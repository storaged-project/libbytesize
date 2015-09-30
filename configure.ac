# configure.ac for libbytesize

AC_INIT([libbytesize], [0.1], [vpodzime@redhat.com])

# Disable building static libraries.
# This needs to be set before initializing automake
AC_DISABLE_STATIC

AM_INIT_AUTOMAKE([foreign -Wall -Werror -Wno-syntax -Wno-portability])
AC_CONFIG_MACRO_DIR([m4])

AM_PROG_AR
AC_PROG_CC

LT_INIT

AC_CONFIG_FILES([Makefile src/Makefile])

LIBBYTESIZE_PKG_CHECK_MODULES([GLIB], [glib-2.0 >= 2.42.2])
LIBBYTESIZE_PKG_CHECK_MODULES([GOBJECT], [gobject-2.0 >= 2.42.2])

m4_ifdef([GOBJECT_INTROSPECTION_CHECK],
[GOBJECT_INTROSPECTION_CHECK([1.3.0])],
[found_introspection=no
AM_CONDITIONAL(HAVE_INTROSPECTION, false)])

# Complain if introspection was not enabled
AS_IF([test "x$found_introspection" = xyes], [:],
      [LIBBYTESIZE_SOFT_FAILURE([GObject introspection must be enabled])])

AC_CHECK_LIB(gmp, __gmpz_init)

AC_CHECK_HEADERS([langinfo.h gmp.h],
                 [],
                 [LIBBYTESIZE_SOFT_FAILURE([Header file $ac_header not found.])],
                 [])

AC_OUTPUT
LIBBYTESIZE_FAILURES
