#!/bin/bash

# Every script should have thisj
set +e

DOCS_SHA=$(git rev-parse --short HEAD)

# Create a temp directory, so we don't get raced by the filesystem
WIKI_DIR=`mktemp -d`

CLONE_URL="git@github.com:illinois-cs241/${TRAVIS_REPO_SLUG}.git"
echo "Cloning $CLONE_URL into $WIKI_DIR"
git clone $CLONE_URL $WIKI_DIR

# If we get race condition on read only files, we need to fix our build system
# no temp directory here

echo "Generating Wiki"
python3 _scripts/gen_wiki.py order.yaml ${WIKI_DIR}

cd ${WIKI_DIR}

git add -A
git commit -m "Updating wiki to ${DOCS_SHA}"
git push origin

cd ${TRAVIS_BUILD_DIR}
