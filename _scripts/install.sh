#!/bin/bash

set -o errexit

# Install packages that we need for python. Python3.6 is already installed
pip install -r requirements.txt

if test $BUILD_FOCUS = "WIKI" || test $BUILD_FOCUS = "EPUB"
then
    # Install pandoc from source because Ubuntu is high outdated
    pushd ~
    wget https://github.com/jgm/pandoc/releases/download/2.7/pandoc-2.7-1-amd64.deb
    sudo dpkg -i pandoc-2.7-1-amd64.deb
    popd
fi;

if test $BUILD_FOCUS = "PDF"
then
    sudo apt update
    sudo apt install texlive-full
fi;
