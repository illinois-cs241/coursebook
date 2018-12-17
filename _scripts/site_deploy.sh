#!/bin/bash

set -e;
set -x;
git config --global core.sshCommand "ssh -i /tmp/deploy_site -F /dev/null"
git clone -b develop --depth 1 git@github.com:illinois-cs241/illinois-cs241.github.io.git ${CLONE_DIR}
git submodule update --init --recursive --depth 200
git submodule sync
cd ${CLONE_DIR}
git checkout develop
cd _wikibook_project/
echo $(pwd)
git status
ls
git pull origin master
export DOCS_SHA=$(git rev-parse --short HEAD)
cd ..
git add _wikibook_project/
git commit -m "Updating docs to ${DOCS_SHA}" || true
git push origin develop

cd ${TRAVIS_BUILD_DIR}
