#!/bin/bash

# Every script should have thisj
set +e

# see if token is passed in through the command line and set
if [ -z ${1+DOES_NOT_EXIST} ]; then
    echo "TOKEN UNSET";
    exit 1;
fi

export DOCS_SHA=$(git rev-parse --short HEAD)

# Create a temp directory, so we don't get raced by the filesystem
WIKI_DIR=`mktemp -d`

CLONE_URL=`https://github.com/${TRAVIS_REPO_SLUG}.wiki.git`
echo "Cloning $CLONE_URL into $WIKI_DIR"
git clone $CLONE_URL ${WIKI_DIR}

# If we get race condition on read only files, we need to fix our build system
# no temp directory here

echo "Generating Wiki"
python3 _scripts/gen_wiki.py order.yaml ${WIKI_DIR}


cd ${WIKI_DIR}

git config credential.helper "store --file=.git/credentials"
echo "https://bhuvy2:${1}@github.com" > .git/credentials 2>/dev/null
git config --global user.email "bhuvan.venkatesh21@gmail.com"
git config --global user.name "Bhuvan Venkatesh"

git add -A
git commit -m "Updating wiki to ${DOCS_SHA}"
git push origin

cd ${TRAVIS_BUILD_DIR}
