#!/usr/bin/env bash

# build the docs
cd docs
make clean
make html
# package the docs
cd _build/html
tar czf ~/html.tgz .
cd ../../..
# checkout doc branch
git checkout gh-pages
# clear out old docs
git rm -rf .
rm -fr docs
rm -fr .idea

tar xzf ~/html.tgz
# commit and push new docs
git add .
git commit -a -m "publish the docs"
git push origin gh-pages

git checkout master