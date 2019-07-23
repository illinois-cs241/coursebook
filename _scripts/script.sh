#!/bin/bash

set -o errexit;

if test $BUILD_FOCUS = "WIKI"
then
    echo "Dummy Step"
elif test $BUILD_FOCUS = "EPUB"
then
    pandoc --toc -s -f latex main.tex -t epub --filter pandoc-citeproc --filter _scripts/pandoc_epub_filter.py -M link-citations=true --epub-cover-image _images/cover.png -M author="B. Venkatesh, L. Angrave, et Al." -o main.epub
else
    make
fi;

