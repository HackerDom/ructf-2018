#!/bin/bash
set -uox pipefail

CHECKER_DIR=$PWD
pushd ../../services/thinkerer
bazel build //checker:all
cp bazel-bin/checker/checker $CHECKER_DIR/thinkerer_checker
popd
