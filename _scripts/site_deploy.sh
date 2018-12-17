#!/bin/bash

set -e;

git config --global core.sshCommand "ssh -i /tmp/deploy_site -F /dev/null"
git clone -b develop --depth 1 git@github.com:illinois-cs241/illinois-cs241.github.io.git ${CLONE_DIR}
cd ${CLONE_DIR}
git submodule update --init --recursive
git submodule update --recursive --depth 200

ls _wikibook_project/
git checkout develop
cd _wikibook_project/
git pull origin master
export DOCS_SHA=$(git rev-parse --short HEAD)
cd ..
git add _wikibook_project/
git commit -m "Updating docs to ${DOCS_SHA}" || true
git push origin develop

cd ${TRAVIS_BUILD_DIR}
