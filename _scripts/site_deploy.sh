#!/bin/bash

set -e;

# Set up ssh
git config --global core.sshCommand "ssh -i /tmp/deploy_site -F /dev/null"

# Clone with submodules
git clone -b develop --depth 1 git@github.com:illinois-cs241/illinois-cs241.github.io.git ${CLONE_DIR}
cd ${CLONE_DIR}
git submodule update --init --recursive

# We need more than one commit because of broken head statuses
git submodule update --recursive --depth 200

# Go to coursebook and checkout
git checkout develop
cd _coursebook/

# Update and store latest sha
git pull origin master
export DOCS_SHA=$(git rev-parse --short HEAD)
cd ..

# Add update, and commit
git add _coursebook/
git commit -m "Updating docs to ${DOCS_SHA}" || true
git push origin develop

# Go back to the build dir
cd ${TRAVIS_BUILD_DIR}
