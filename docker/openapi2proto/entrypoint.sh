#!/bin/sh

if [[ -z $1 ]]; then
    echo 'Provide a file name'
    exit 1
fi

openapi2proto -spec /app/$1.json -annotate  -out /app/$1.proto

exit $?