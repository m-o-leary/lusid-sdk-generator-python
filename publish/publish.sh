#!/bin/bash -e

if [[ (${#1} -eq 0) ]] ; then
    echo
    echo "[ERROR] missing API key"
    echo
    exit 1
fi

if [[ (${#2} -eq 0) ]] ; then
    echo 
    echo "[ERROR] missing PyPi repo"
    echo
    exit 1
fi

if [[ (${#3} -eq 0) ]] ; then
    echo 
    echo "[ERROR] missing library name"
    echo
    exit 1
fi

pypi_password=$1
pypi_repo=$2
library_name=$3

cd sdk

api_version=$(cat ${library_name}/__init__.py | grep __version__ |  awk '{split($0, a, "="); print a[2]}' | tr -d ' "')

# update pip
pip install --upgrade pip

# packages to install
pip install twine wheel
python setup.py sdist
python setup.py bdist_wheel

# upload
twine upload --repository-url $pypi_repo -u pypi -p $pypi_password dist/*
# twine upload  -u finbourne -p $pypi_password dist/*

cd ..

rm -f publish.sh