PDF_TARGETS = paper.pdf

TEX_STUFF = $(wildcard *.tex) $(wildcard *.sty) $(wildcard *.cls) \
	    $(wildcard Figures/*.pdf) $(wildcard Graphs/*.pdf)

HTLATEX = htlatex
PDFLATEX = pdflatex -shell-escape

all: $(PDF_TARGETS)

%.aux: %.tex $(TEX_STUFF)
	$(PDFLATEX) $*

%.bbl: %.aux
	bibtex $* || true

%.pdf: %.bbl
	$(PDFLATEX) $*
	$(PDFLATEX) $*
	$(PDFLATEX) $*

clean:
	rm -f *.ent *.aux *.log *.bbl *.blg *.out $(PDF_TARGETS)
	rm -f *.4ct *.4ct *.css *.fls *.idv *.lg *.tmp *.xref

.PRECIOUS: .bbl .aux
