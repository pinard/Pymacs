PYTHON = python

p = builddir
e = $p/.estampille

all: $p/pymacs.ps
	gv -antialias $<

dvi: $p/pymacs.dvi
	cp $p/pymacs.dvi .

info: $p/pymacs.info
	cp $p/pymacs.info .

pdf: $p/pymacs.pdf
	cp $p/pymacs.pdf .

ps: $p/pymacs.ps
	cp $p/pymacs.ps .

$p/pymacs.info: $p/pymacs.texi
	makeinfo --force $<

$p/pymacs.dvi: $p/pymacs.texi
	cd $p && TEXINPUTS=.. texi2dvi pymacs.texi

$p/pymacs.pdf: $p/pymacs.texi
	cd $p && TEXINPUTS=.. texi2pdf pymacs.texi

$p/pymacs.ps: $p/pymacs.dvi
	cd $p && dvips -tletter -o- pymacs.dvi > pymacs.ps

$p/pymacs.texi: pymacs.all $e
	PYTHONPATH=.. $(PYTHON) ../scripts/allout texi pymacs.all > $@-tmp
	mv $@-tmp $@

$e:
	install -d $p
	@touch $e
