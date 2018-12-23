#!/bin/bash

set -e;

if test $BUILD_FOCUS = WIKI; then
    export NUM_RETRIES=3;
    export BUILD_TIME=10;
    export CLONE_DIR=`mktemp -d`;
    bash _scripts/push_to_wiki.sh;
else
    TMP_FILE=`mktemp`;
    cp main.pdf $TMP_FILE;
    git config --global core.sshCommand "ssh -i /tmp/deploy_wiki -F /dev/null";
    git checkout --orphan pdf_deploy;
    rm -rf *;
    cp $TMP_FILE coursebook.pdf;
    git add coursebook.pdf;
    git commit -m "Adding coursebook";
    OLD_ORIGIN=`git remote get-url origin`;
    git remote set-url origin git@github.com:${TRAVIS_REPO_SLUG}.git;
    git push origin --force pdf_deploy;
    git remote set-url origin ${OLD_ORIGIN};
fi

