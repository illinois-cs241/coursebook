# Find all tex files one directory down
TEX=$(shell find . -maxdepth 2 -mindepth 2 -path "./.git*" -prune -o -type f -iname "*.tex" -print)
MAIN_TEX=main.tex
PDF_TEX=$(patsubst %.tex,%.pdf,$(MAIN_TEX))
BASE=$(patsubst %.tex,%,$(MAIN_TEX))
OTHER_FILES=$(addprefix $(BASE),.aux .log .synctex.gz .toc .out .blg .bbl .glg .gls .ist .glo)
BIBS=$(shell find . -maxdepth 2 -mindepth 2 -path "./.git*" -prune -o -type f -iname "*.bib" -print)
LATEX_COMMAND=pdflatex -quiet -synctex=1 -interaction=nonstopmode $(MAIN_TEX) > /dev/null 2>&1
OTHER=$$(find . -iname *aux) $$(find . -iname *bbl) $$(find . -iname *blg)
.PHONY: all
all: $(PDF_TEX)


$(PDF_TEX): $(TEX) $(MAIN_TEX) $(BIBS) Makefile
	-latexmk latexmk -interaction=nonstopmode -quiet -f -pdf $(MAIN_TEX) 2>&1 >/dev/null
	-@latexmk -c
	-@rm *aux *bbl *glg *glo *gls *ist *latexmk *fls

.PHONY: clean
clean:
	-@rm $(PDF_TEX) $(OTHER_FILES) $(OTHER)
