#!/bin/sh

# this is supposed to be used from within the package root dir,
#   too lazy to make it more general

echo "building package"
python -m build

echo "uploading to pypi"
twine upload dist/*

echo "removing dist/*"
rm -r dist