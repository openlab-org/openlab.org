#!/bin/bash
. "`dirname \"$0\"`/functions.sh"

cd $MY_PATH
cd ../..

ack . -l --python --html | entr python ./manage.py test
