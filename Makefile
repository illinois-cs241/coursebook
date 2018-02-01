# Find all tex files one directory down
TEX=$(shell find . -maxdepth 2 -mindepth 2 -path "./.git*" -prune -o -type f -iname "*.tex" -print)
MAIN_TEX=main.tex
PDF_TEX=$(patsubst %.tex,%.pdf,$(MAIN_TEX))
BASE=$(patsubst %.tex,%,$(MAIN_TEX))
OTHER_FILES=$(addprefix $(BASE),.aux .log .synctex.gz .toc .out .blg .bbl .glg .gls .glsdefs .ist .glo)
BIBS=$(shell find . -maxdepth 2 -mindepth 2 -path "./.git*" -prune -o -type f -iname "*.bib" -print)
LATEX_COMMAND=pdflatex -quiet -synctex=1 -interaction=nonstopmode $(MAIN_TEX) > /dev/null 2>&1
.PHONY: all
all: $(PDF_TEX)


$(PDF_TEX): $(TEX) $(MAIN_TEX) $(BIBS)
	-@rm $(PDF_TEX)
	-$(LATEX_COMMAND)
	-makeglossaries $(BASE)
	for i in "*aux"; do bibtex $$i; done;
	-$(LATEX_COMMAND)
	-$(LATEX_COMMAND)
	-@if [ -f $(MAIN_TEX) ]; then echo $(MAIN_TEX) Made!; else exit 1; fi;
	-@rm $(OTHER_FILES)

.PHONY: clean
clean:
	-@rm $(PDF_TEX)
