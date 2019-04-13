if WITH_TOOLS
dist_noinst_SCRIPTS = bs_calc.py

dist_man1_MANS = bscalc.man

install-exec-local:
	install -d ${DESTDIR}${bindir}
	install -m0755 ${srcdir}/bs_calc.py ${DESTDIR}${bindir}/bscalc

uninstall-local:
	rm ${DESTDIR}${bindir}/bscalc
endif
