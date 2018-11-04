#!/bin/bash

# script to automate roxly merge typical case
#   gb april17

set -e

if [[ $# < 1 || $# > 2 ]]; then
    echo "Usage: $0 dropbox://file/path [local_repo]"
    echo "Usage: default local_repo is pwd"
    exit 1
fi

dbx_url=$1
if [[ $# == 2 ]]; then
    repo=$2
else
    repo=$(pwd)
fi

oxsite=dropbox
IFS=':' read -ra split <<< "$dbx_url"
site="${split[0]}"
fp=$(echo "${split[1]}" | sed 's,//,,')
if [[ $oxsite != "$site" ]]; then
    echo "Usage: $0 dropbox://file/path [local_repo]"
    echo "Usage: default local_repo is pwd"
    exit 1
fi

if [[ ! -d $repo ]]; then
    mkdir $repo
    cd $repo
fi

roxlycmd=roxly
nlog=5

$roxlycmd --version

echo "Cloning $dbx_url into $(pwd) ..."
$roxlycmd clone $dbx_url

echo "Viewing metadata latest 2 revisions (cached locally) ..."
$roxlycmd log --oneline --recent 2 $fp

echo "Viewing metadata least latest 2 revisions (cached locally) ..."
$roxlycmd log --oneline $fp | tail -2

echo "Merging latest 2 revisions data ..."
$roxlycmd merge $fp

echo "Pushing merged revision data ..."
$roxlycmd push --add $fp
