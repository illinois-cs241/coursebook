#!/bin/bash

set -o errexit

if test $BUILD_FOCUS = "WIKI"
then
    # Install pandoc from source because Ubuntu is high outdated
    pushd ~
    wget https://github.com/jgm/pandoc/releases/download/2.7/pandoc-2.7-1-amd64.deb
    sudo dpkg -i pandoc-2.7-1-amd64.deb
    popd

    # Install packages that we need for python. Python3.6 is already installed
    pip install -r requirements.txt
else
    echo "Dummy step"
fi;

