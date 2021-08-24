if WITH_PYTHON3
py3libdir = $(shell python3 -c "import sysconfig; print(sysconfig.get_path('platlib', vars={'platbase': '${exec_prefix}'}))")
py3bytesizedir    = $(py3libdir)/bytesize
dist_py3bytesize_DATA = bytesize.py __init__.py
endif

MAINTAINERCLEANFILES = Makefile.in
