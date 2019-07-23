#!/bin/bash

set -e;

if test $BUILD_FOCUS = WIKI; then
    # Set environment variables used in the next script
    export NUM_RETRIES=3;
    export BUILD_TIME=10;
    export CLONE_DIR=`mktemp -d`;

    # Run the actual script
    bash _scripts/push_to_wiki.sh;
elif test $BUILD_FOCUS = "EPUB"
    ls
else
    # Copy main to a tempfile, so we don't get any checkout errors
    TMP_DIR=`mktemp -d`;
    find . -maxdepth 2 -iname "*.pdf" -exec mv {} $TMP_DIR \;

    # Set up ssh 
    git config --global core.sshCommand "ssh -i /tmp/deploy_wiki -F /dev/null";

    # Grab an orphaned branch, so git doesn't calculate diffs
    git checkout --orphan pdf_deploy;

    # Remove all other files, we won't need them
    rm -rf * || true;
    rm -rf .github .gitattributes .gitignore || true;

    # Move the tempfile back to the coursebook pdf
    mv $TMP_DIR/* .;

    # Git add commit
    git add -A;
    git commit -m "Adding build on $(date)";

    # Swap the https origin for the ssh origin so we can push
    OLD_ORIGIN=`git remote get-url origin`;
    git remote set-url origin git@github.com:${TRAVIS_REPO_SLUG}.git;
    git push origin --force pdf_deploy;

    # Swap it back
    git remote set-url origin ${OLD_ORIGIN};
fi

