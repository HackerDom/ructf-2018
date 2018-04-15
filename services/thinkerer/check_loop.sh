#!/bin/bash
set -x



pushd bazel-bin/checker

while true
do
    ./checker check $1
    [ $? != 101 ] && exit 1
    ./checker put $1 test1 test1
    [ $? != 101 ] && exit 1
    ./checker get $1 test1 test1
    [ $? != 101 ] && exit 1

    ./checker put $1 test1 test1 1
    [ $? != 101 ] && exit 1
    ./checker get $1 test1 test1 1
    [ $? != 101 ] && exit 1

    ./checker put $1 test1 test1 2
    [ $? != 101 ] && exit 1
    ./checker get $1 test1 test1 2
    [ $? != 101 ] && exit 1


done

popd
