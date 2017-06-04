#!/bin/bash
set -e

if [ -n "$1" ];
then
    C="$1"
else
    C="/tmp/ol_random_photos/"
    mkdir -p $C
fi

cd $C
COUNTER=50


# turn off die on error
set +e

while [  `ls -1 | wc -l` -lt 50 ]; do
    wget http://lorempixel.com/400/400/abstract
    wget http://lorempixel.com/400/400/business
    wget http://lorempixel.com/400/400/transport
    let COUNTER-=1
    let r="$((RANDOM%100+300))"
    wget http://placekitten.com/400/$r
    wget http://www.fillmurray.com/300/$r
    wget http://baconmockup.com/200/$r
    wget http://placebear.com/400/$r
    #wget http://placedog.com/400/$r # BROKEN
    # one huge one
    wget http://lorempixel.com/1300/1300/technics
done

find . -type f -exec mv '{}' '{}'.jpg \;

