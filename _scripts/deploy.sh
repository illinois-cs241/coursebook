#!/bin/bash

if test $BUILD_FOCUS = WIKI; then
    export NUM_RETRIES=3;
    export BUILD_TIME=10;
    export CLONE_DIR=`mktemp -d`;
    bash _scripts/push_to_wiki.sh;
else
    TMP_FILE=`mktemp`;
    cp main.pdf $TMP_FILE;
    git config --global core.sshCommand "ssh -i /tmp/deploy_pdf -F /dev/null";
    git checkout -b pdf_deploy;
    cp $TMP_FILE coursebook.pdf;
    git add coursebook.pdf;
    git commit -m "Adding coursebook";
    git push origin pdf_deploy;
fi
