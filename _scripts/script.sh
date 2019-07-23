#!/bin/bash

set -o errexit;

if test $BUILD_FOCUS = "WIKI"
then
    echo "Dummy Step"
elif test $BUILD_FOCUS = "EPUB"
then
    make epub;
else
    make
fi;

