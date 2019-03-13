#!/bin/bash

set -o errexit

if test $BUILD_FOCUS = "WIKI"
then
    pushd ~
    wget https://github.com/jgm/pandoc/releases/download/2.7/pandoc-2.7-1-amd64.deb
    ls
    sudo dpkg -i pandoc-2.7.1-amd64.deb
    popd
    pip install -r requirements.txt
else
    echo "Dummy step"
fi;

