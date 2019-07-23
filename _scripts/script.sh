#!/bin/bash

set -o errexit;

if test $BUILD_FOCUS = "WIKI"
then
    echo "Generating Wiki"
    mkdir -p _wiki
    python3 _scripts/gen_wiki.py order.yaml _wiki
elif test $BUILD_FOCUS = "EPUB"
then
    make epub;
else
    make pdf;
fi;

