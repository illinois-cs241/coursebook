# Find all tex files one directory down
TEX=$(shell find . -maxdepth 2 -mindepth 2 -path "./.git*" -prune -o -type f -iname "*.tex" -print)
MAIN_TEX=main.tex
PDF_TEX=$(patsubst %.tex,%.pdf,$(MAIN_TEX))
OTHER_FILES=$(patsubst %.tex,%.aux,$(MAIN_TEX)) $(patsubst %.tex,%.log,$(MAIN_TEX)) $(patsubst %.tex,%.synctex.gz,$(MAIN_TEX))
.PHONY: all
all: $(PDF_TEX)

$(PDF_TEX): $(TEX) $(MAIN_TEX)
	-@pdflatex -synctex=1 -interaction=nonstopmode $(MAIN_TEX)
	-@rm $(OTHER_FILES)

.PHONY: clean
clean:
	-@rm $(PDF_TEX)