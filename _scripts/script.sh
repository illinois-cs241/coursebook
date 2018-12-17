#!/bin/bash

if test $BUILD_FOCUS = "WIKI"
then
    echo "Dummy Step"
else
    make
fi;

