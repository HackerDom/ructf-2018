FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y git build-essential clang unzip wget
RUN wget -c https://github.com/bazelbuild/bazel/releases/download/0.17.1/bazel-0.17.1-installer-linux-x86_64.sh
RUN bash bazel-0.17.1-installer-linux-x86_64.sh
COPY thinkerer /thinkerer/thinkerer
COPY proto /thinkerer/proto
COPY WORKSPACE /thinkerer/
WORKDIR /thinkerer
RUN ls -lh
RUN bazel build //thinkerer:all
RUN mkdir -p /thinkerer/data
RUN cp /thinkerer/bazel-bin/thinkerer/server /thinkerer/server

ENTRYPOINT /thinkerer/server
EXPOSE 50051
