#
# ${R_HOME}/src/Makefile


srcdir = .
top_srcdir = ..

top_builddir = ..
subdir = src

include $(top_builddir)/Makeconf

distdir = $(top_builddir)/$(PACKAGE)-$(VERSION)/$(subdir)
DISTFILES = Makefile.in

## need extra early to get libintl.h installed
SUBDIRS = scripts include extra appl nmath unix main modules library
SUBDIRS_WITH_NO_BUILD = gnuwin32

all: Makefile R

Makefile: $(srcdir)/Makefile.in $(top_builddir)/config.status
	@cd $(top_builddir) && $(SHELL) ./config.status $(subdir)/$@

R: Makefile

install install-strip TAGS info dvi dist check R docs:
	@for d in $(SUBDIRS); do \
	  (cd $${d} && $(MAKE) $@) || exit 1; \
	done

uninstall mostlyclean clean:
	@(for d in $(SUBDIRS); do rsd="$${d} $${rsd}"; done; \
	  for d in $${rsd}; do (cd $${d} && $(MAKE) $@); done)
distclean:
	@(for d in $(SUBDIRS); do rsd="$${d} $${rsd}"; done; \
	  for d in $${rsd}; do (cd $${d} && $(MAKE) $@); done)
	-@rm -f Makefile
maintainer-clean: distclean

distdir: $(DISTFILES)
	@for f in $(DISTFILES); do \
	  test -f $(distdir)/$${f} \
	    || ln $(srcdir)/$${f} $(distdir)/$${f} 2>/dev/null \
	    || cp -p $(srcdir)/$${f} $(distdir)/$${f}; \
	done
	@for d in $(SUBDIRS); do \
	  test -d $(distdir)/$${d} \
	    || mkdir $(distdir)/$${d} \
	    || exit 1; \
	  chmod 755 $(distdir)/$${d}; \
	  (cd $${d} && $(MAKE) distdir) \
	    || exit 1; \
	done
	@for d in $(SUBDIRS_WITH_NO_BUILD); do \
	  ((cd $(srcdir); $(TAR) -c -f - --exclude=.svn --exclude=CVS $${d}) \
	      | (cd $(distdir); $(TAR) -x -f -)) \
	    || exit 1; \
	done
