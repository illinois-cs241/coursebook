#!/bin/bash

set -o errexit;

if test $BUILD_FOCUS = "WIKI"
then
    echo "Dummy Step"
else
    make
fi;

