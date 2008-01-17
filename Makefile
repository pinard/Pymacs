PACKAGE = pymacs
VERSION = 0.1

FILES = README TODO Makefile pymacs.el pymacs.py pymacs-services \
pymacs-test.el pymacs_test.py

install:
	install -m 644 pymacs.el $(HOME)/share/emacs/lisp
	install -m 644 pymacs.py $(HOME)/share/python
	install -m 755 pymacs-services $(HOME)/bin
	install -m 644 pymacs-test.el $(HOME)/share/emacs/lisp
	install -m 644 pymacs_test.py $(HOME)/share/emacs/python

dist:
	mkdir $(PACKAGE)-$(VERSION)
	cp -p $(FILES) $(PACKAGE)-$(VERSION)
	tar cfz $(PACKAGE)-$(VERSION).tar.gz $(PACKAGE)-$(VERSION)
	rm -rf $(PACKAGE)-$(VERSION)
