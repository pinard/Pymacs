# Interface between Emacs Lisp and Python - Makefile.
# Copyright © 2001, 2002, 2003 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

EMACS = emacs
PYTHON = python
RST2LATEX = rst2latex

PYSETUP = $(PYTHON) setup.py
P4 = $(PYTHON) p4 -C p4config.py

all:
	$(P4) *.in Pymacs contrib tests
	$(PYSETUP) build

check: clean-debug
	$(P4) pymacs.el.in Pymacs tests
	cd tests && \
	  EMACS="$(EMACS)" PYTHON="$(PYTHON)" \
	  PYMACS_OPTIONS="-d debug-protocol -s debug-signals" \
	  $(PYTHON) pytest -f t $(TEST)

install:
	$(P4) *.in Pymacs contrib tests
	$(PYSETUP) install

clean: clean-debug
	rm -rf build* contrib/rebox/build
	rm -f */*py.class */*.pyc p4.pdf pymacs.pdf
	$(P4) -c *.in Pymacs contrib tests

clean-debug:
	rm -f tests/debug-protocol tests/debug-signals

p4.pdf: p4.rst.in
	$(P4) p4.rst.in
	rm -rf tmp-pdf
	mkdir tmp-pdf
	$(RST2LATEX) --use-latex-toc --input-encoding=UTF-8 \
	  p4.rst tmp-pdf/p4.tex
	cd tmp-pdf && pdflatex p4.tex
	cd tmp-pdf && pdflatex p4.tex
	mv -f tmp-pdf/p4.pdf $@
	rm -rf tmp-pdf

pymacs.pdf: pymacs.rst.in
	$(P4) pymacs.rst.in
	rm -rf tmp-pdf
	mkdir tmp-pdf
	$(RST2LATEX) --use-latex-toc --input-encoding=UTF-8 \
	  pymacs.rst tmp-pdf/pymacs.tex
	cd tmp-pdf && pdflatex pymacs.tex
	cd tmp-pdf && pdflatex pymacs.tex
	mv -f tmp-pdf/pymacs.pdf $@
	rm -rf tmp-pdf

# The following goals for the maintainer of the Pymacs Web site.

push: local
	find -name '*~' | xargs rm -fv
	push alcyon -d entretien/pymacs
	ssh alcyon 'make-web -C entretien/pymacs/web'

local: p4.pdf pymacs.pdf pymacs.rst
	make-web -C web

VERSION = `grep '^version' setup.py | sed -e "s/'$$//" -e "s/.*'//"`

publish:
	version=$(VERSION) && \
	  git archive --format=tar --prefix=Pymacs-$$version/ HEAD . \
	    | gzip > web/archives/Pymacs-$$version.tar.gz

official: publish
	rm -f web/archives/Pymacs.tar.gz
	version=$(VERSION) && \
	  ln -s Pymacs-$$version.tar.gz web/archives/Pymacs.tar.gz
