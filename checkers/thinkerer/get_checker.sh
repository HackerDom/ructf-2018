#!/bin/bash -x
set -uox pipefail

CHECKER_DIR=$PWD
CHECKER=$CHECKER_DIR/thinkerer_checker

pushd ../../services/thinkerer
docker build -t thinkerer_checker_builder -f Dockerfile.checker .
docker run --rm --entrypoint cat thinkerer_checker_builder /thinkerer/bazel-bin/checker/checker > $CHECKER.new
chmod +x $CHECKER.new
mv $CHECKER.new $CHECKER
popd
