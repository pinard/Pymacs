# Interface between Emacs Lisp and Python - Makefile.
# Copyright © 2001, 2002, 2003 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

# The `README' file provides a few good hints about installation.

### Start of customisation.
#
# Somewhere on your Emacs Lisp load-path.
lispdir =
#
### End of customisation.

VERSION = 0.23-beta3
PYSETUP = python setup.py

all: pymacs.el Pymacs/__init__.py
	$(PYSETUP) build

check: pymacs.el Pymacs/__init__.py
	cd tests && ./pytest $(TEST)

install: pymacs.el Pymacs/__init__.py
	./setup -l '$(lispdir)'
	$(PYSETUP) install

tags:
	(find bin -type f; find -name '*.py') | grep -v '~$$' | etags -

clean:
	rm -rf build* Pymacs/*.pyc tests/*.pyc

pymacs.el: pymacs.el.in Makefile
	rm -f $@
	sed 's/@VERSION@/$(VERSION)/g' pymacs.el.in > $@-tmp
	mv $@-tmp $@
	chmod -w $@

Pymacs/__init__.py: __init__.py.in Makefile
	rm -f $@
	sed 's/@VERSION@/$(VERSION)/g' __init__.py.in > $@-tmp
	mv $@-tmp $@
	chmod -w $@

# The following goals for the maintainer of the Pymacs Web site.

official: publish
	ln -s Pymacs-$(VERSION).tar.gz web/archives/Pymacs.tar.gz

publish: web/pymacs.pdf web/pymacs.rst
	rm -f web/archives/Pymacs.tar.gz
	git archive --format=tar --prefix=Pymacs-$(VERSION)/ HEAD . \
	  | gzip > web/archives/Pymacs-$(VERSION).tar.gz

synchro: web/pymacs.pdf web/pymacs.rst
	ajuster-web web
	git gc --prune
	find -name '*~' | xargs rm -fv
	synchro -PD alcyon entretien

web/pymacs.pdf: web/pymacs.rst
	rm -rf tmp-pdf
	mkdir tmp-pdf
	rst2latex.py --use-latex-toc --input-encoding=UTF-8 \
	  web/pymacs.rst tmp-pdf/pymacs.tex
	cd tmp-pdf && pdflatex pymacs.tex
	cd tmp-pdf && pdflatex pymacs.tex
	mv -f tmp-pdf/pymacs.pdf $@
	rm -rf tmp-pdf

web/pymacs.rst: pymacs.rst.in Makefile
	rm -f $@
	sed 's/@VERSION@/$(VERSION)/g' pymacs.rst.in > $@-tmp
	mv $@-tmp $@
	chmod -w $@
