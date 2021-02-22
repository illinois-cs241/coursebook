#!/bin/bash

# Every script should have this
set -e

DOCS_SHA=$(git rev-parse --short HEAD)

# Create a temp directory, so we don't get raced by the filesystem
WIKI_DIR=`mktemp -d`

CLONE_URL="git@github.com:${GITHUB_REPOSITORY}.wiki.git"
echo "Cloning $CLONE_URL into $WIKI_DIR"
git config --global core.sshCommand "ssh -i /tmp/deploy_wiki -F /dev/null"
git clone $CLONE_URL $WIKI_DIR

# If we get race condition on read only files, we need to fix our build system
# no temp directory here

echo "Copying Wiki"
cp _wiki/* ${WIKI_DIR}

cd ${WIKI_DIR}

#git add -A
#git commit -m "Updating wiki to ${DOCS_SHA}" --author "$COMMITTER_EMAIL <$AUTHOR_NAME>" || true
#git push origin

# For testing, just test out the SSH key
ssh -i /tmp/deploy_wiki -T git@github.com

cd ${GITHUB_WORKSPACE}


# Part 2, Update the site
bash _scripts/site_deploy.sh
