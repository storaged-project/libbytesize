if WITH_PYTHON2
pylibdir = $(shell python -c "import distutils.sysconfig; print(distutils.sysconfig.get_python_lib(1,0,prefix='${exec_prefix}'))")

pybytesizedir     = $(pylibdir)/bytesize
dist_pybytesize_DATA = bytesize.py __init__.py
endif

if WITH_PYTHON3
py3libdir = $(shell python3 -c "import distutils.sysconfig; print(distutils.sysconfig.get_python_lib(1,0,prefix='${exec_prefix}'))")
py3bytesizedir    = $(py3libdir)/bytesize
nodist_py3bytesize_DATA = bytesize.py __init__.py
endif

MAINTAINERCLEANFILES = Makefile.in
