# Interface between Emacs LISP and Python - Makefile.
# Copyright © 2001 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

### Start of customisation.
#

# Somewhere on your shell PATH.
bindir = $(HOME)/bin

# Somewhere on your Emacs LISP load-path.
lispdir = $(HOME)/share/emacs/lisp

# Somewhere on your Python sys.path.
pythondir = $(HOME)/share/python

# Directory for Python extensions.  Make it empty if you do not use one!
pymacsdir = $(HOME)/share/emacs/python

#
### End of customisation.

PACKAGE = pymacs
VERSION = 0.4

FILES = ChangeLog Makefile README TODO elc pyc pymacs.el pymacs.py \
pymacs-services pymacs-test.el pymacs_test.py

install:
	sed 's,@VERSION@,$(VERSION),' pymacs.el > x.pymacs.el
	sed 's,@VERSION@,$(VERSION),' pymacs.py > x.pymacs.py
	sed 's,@pymacsdir@,$(pymacsdir),' pymacs-services > x.pymacs-services
	install -m 644 x.pymacs.el $(lispdir)/pymacs.el
	install -m 644 x.pymacs.py $(pythondir)/pymacs.py
	install -m 755 x.pymacs-services $(bindir)/pymacs-services
	rm -f x.pymacs.el x.pymacs.py x.pymacs-services
	./elc $(lispdir)/pymacs.el
	./pyc $(pythondir)/pymacs.py
	if test -n "$(pymacsdir)" && test -d "$(pymacsdir)"; then \
	  install -m 644 pymacs-test.el $(lispdir); \
	  install -m 644 pymacs_test.py $(pymacsdir); \
	fi

dist:
	mkdir $(PACKAGE)-$(VERSION)
	cp -p $(FILES) $(PACKAGE)-$(VERSION)
	tar cfz $(PACKAGE)-$(VERSION).tar.gz $(PACKAGE)-$(VERSION)
	rm -rf $(PACKAGE)-$(VERSION)
	chmod 644 $(PACKAGE)-$(VERSION).tar.gz
	scp -p $(PACKAGE)-$(VERSION).tar.gz bor:pymacs/
