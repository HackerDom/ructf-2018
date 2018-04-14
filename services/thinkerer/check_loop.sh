#!/bin/bash
set -x

pushd bazel-bin/checker

while true
do
    ./checker check localhost
    [ $? != 101 ] && exit 1
    ./checker put localhost test1 test1
    [ $? != 101 ] && exit 1
    ./checker get localhost test1 test1
    [ $? != 101 ] && exit 1

    ./checker put localhost test1 test1 1
    [ $? != 101 ] && exit 1
    ./checker get localhost test1 test1 1
    [ $? != 101 ] && exit 1

    ./checker put localhost test1 test1 2
    [ $? != 101 ] && exit 1
    ./checker get localhost test1 test1 2
    [ $? != 101 ] && exit 1


done

popd
