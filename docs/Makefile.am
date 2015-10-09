all-local: html-doc.stamp

html-doc.stamp: ${srcdir}/libbytesize-docs.xml ${srcdir}/libbytesize-sections.txt ${srcdir}/../src/bs_size.c ${srcdir}/../src/bs_size.h
	touch ${builddir}/html-doc.stamp
	test ${builddir} == ${srcdir} || cp ${srcdir}/libbytesize-sections.txt ${srcdir}/libbytesize-docs.xml ${builddir}
	gtkdoc-scan --rebuild-types --module=libbytesize --source-dir=${srcdir}/../src/
	gtkdoc-mkdb --module=libbytesize --output-format=xml --source-dir=${srcdir}/../src/ --source-suffixes=c,h
	test -d ${builddir}/html || mkdir ${builddir}/html
	(cd ${builddir}/html; gtkdoc-mkhtml libbytesize ${builddir}/../libbytesize-docs.xml)
	gtkdoc-fixxref --module=libbytesize --module-dir=html  --html-dir=/usr/share/gtk-doc/html

clean-local:
	-rm -rf ${builddir}/html
	-rm -rf ${builddir}/xml
	test ! -f ${builddir}/html-doc.stamp || rm ${builddir}/html-doc.stamp
	test ${builddir} == ${srcdir} || rm -f ${builddir}/libbytesize-sections.txt ${builddir}/libbytesize-docs.xml

install-data-local:
	test -d ${DESTDIR}${datadir}/gtk-doc/html/libbytesize || mkdir -p ${DESTDIR}${datadir}/gtk-doc/html/libbytesize
	install -m0644 ${builddir}/html/* ${DESTDIR}${datadir}/gtk-doc/html/libbytesize/

uninstall-local:
	-rm -rf ${DESTDIR}${datadir}/gtk-doc/html/libbytesize/

dist_noinst_DATA = ${srcdir}/libbytesize-sections.txt ${srcdir}/libbytesize-docs.xml

CLEANFILES = html.stamp sgml.stamp \
	libbytesize-decl-list.txt \
	libbytesize-decl.txt \
	libbytesize-decl.txt.bak \
	libbytesize-overrides.txt \
	libbytesize-undeclared.txt \
	libbytesize-undocumented.txt \
	libbytesize-unused.txt \
	libbytesize.types

MAINTAINERCLEANFILES = Makefile.in libbytesize-docs.xml
