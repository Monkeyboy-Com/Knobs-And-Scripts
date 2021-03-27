#!/bin/bash

base=`dirname $0`
cd "$base"
base=`pwd`

name=`basename $0 .sh`

export PYTHONPATH=${base}/lib

echo "${name}: library $PYTHONPATH"
echo ''

cd src

# Use this line to include the access token
#python3 kas.py create --github --private --url https://github.com --name GrayHillDocuments --token d1899d621920279cbef026245e1c31a93c5a8f3e --repo Clavius

# Use this line instead to test prompting for the access token
python3 kas.py create --github --private --url https://github.com --name GrayHillDocuments --repo Clavius
