# configure.ac for libbytesize

AC_INIT([libbytesize], [0.1], [vpodzime@redhat.com])

# Disable building static libraries.
# This needs to be set before initializing automake
AC_DISABLE_STATIC

AM_INIT_AUTOMAKE([foreign -Wall -Werror -Wno-syntax -Wno-portability])
AM_GNU_GETTEXT_VERSION([0.19.1])
AM_GNU_GETTEXT([external])
AC_CONFIG_MACRO_DIR([m4])

AM_PATH_PYTHON

AM_PROG_AR
AC_PROG_CC

LT_INIT

AC_CONFIG_FILES([Makefile src/Makefile po/Makefile.in src/python/Makefile src/python/gi/Makefile src/python/gi/overrides/Makefile])

LIBBYTESIZE_PKG_CHECK_MODULES([GLIB], [glib-2.0 >= 2.42.2])
LIBBYTESIZE_PKG_CHECK_MODULES([GOBJECT], [gobject-2.0 >= 2.42.2])

m4_ifdef([GOBJECT_INTROSPECTION_CHECK],
[GOBJECT_INTROSPECTION_CHECK([1.3.0])],
[found_introspection=no
AM_CONDITIONAL(HAVE_INTROSPECTION, false)])

# Complain if introspection was not enabled
AS_IF([test "x$found_introspection" = xyes], [:],
      [LIBBYTESIZE_SOFT_FAILURE([GObject introspection must be enabled])])

AC_PATH_PROG([PYTHON3], [python3], [no])
AS_IF([test "x$PYTHON3" == "xno"], [LIBBYTESIZE_SOFT_FAILURE([\
      The python3 program was not found in the search path. Please ensure that it is installed and its directory is included in the search path.])],
      [:])

AC_SUBST([PYTHON3_EXEC_PREFIX], ['${exec_prefix}'])
PYTHON3_EXECDIR=`$PYTHON3 -c "import distutils.sysconfig; \
                          print(distutils.sysconfig.get_python_lib(1,0,prefix='$PYTHON3_EXEC_PREFIX'))"`
AC_SUBST(py3execdir, $PYTHON3_EXECDIR)
AM_CONDITIONAL(USE_PYTHON3, test ${use_python3} = "yes")

AC_CHECK_LIB(gmp, __gmpz_init)

AC_CHECK_HEADERS([langinfo.h gmp.h],
                 [],
                 [LIBBYTESIZE_SOFT_FAILURE([Header file $ac_header not found.])],
                 [])

AC_OUTPUT
LIBBYTESIZE_FAILURES
