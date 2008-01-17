PACKAGE = pymacs
VERSION = 0.0

FILES = README Makefile essai.py pymacs.el pymacs.py pymacs-services

install:
	install -m 755 pymacs-services $(HOME)/bin
	install -m 644 pymacs.el essai.py $(HOME)/share/emacs/lisp
	install -m 644 pymacs.py essai.py $(HOME)/share/python

dist:
	mkdir $(PACKAGE)-$(VERSION)
	cp -p $(FILES) $(PACKAGE)-$(VERSION)
	tar cfz $(PACKAGE)-$(VERSION).tar.gz $(PACKAGE)-$(VERSION)
	rm -rf $(PACKAGE)-$(VERSION)
