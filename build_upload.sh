#!/bin/sh

# this is supposed to be used from within the package root dir,
#   too lazy to make it more general

echo "building package"
/bin/python -m build

echo "uploading to pypi"
# alternatively, use /bin/python -m twine, i use twine in arch
/bin/twine upload dist/*

echo "removing dist/*"
rm -r dist