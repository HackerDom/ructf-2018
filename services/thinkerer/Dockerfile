FROM ubuntu:latest as build

RUN sed -i 's|http://archive|http://ru.archive|g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y openjdk-8-jdk curl
RUN echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list
RUN curl https://bazel.build/bazel-release.pub.gpg | apt-key add -
RUN apt-get update
RUN apt-get install -y bazel git build-essential clang
COPY thinkerer /thinkerer/thinkerer
COPY WORKSPACE /thinkerer/
COPY build.sh /thinkerer/
COPY fetch.sh /thinkerer/
WORKDIR /thinkerer
RUN ls -lh
RUN ./fetch.sh
RUN ./build.sh
RUN ldd /thinkerer/bazel-bin/thinkerer/server

FROM ubuntu:latest
WORKDIR /bin
COPY --from=build /thinkerer/bazel-bin/thinkerer/server /bin

ENTRYPOINT /bin/server
EXPOSE 50051
