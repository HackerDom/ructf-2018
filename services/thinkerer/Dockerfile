FROM ubuntu:latest as build

RUN sed -i 's|http://archive|http://ru.archive|g' /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y openjdk-8-jdk curl
RUN echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list
RUN curl https://bazel.build/bazel-release.pub.gpg | apt-key add -
RUN apt-get update
RUN apt-get install -y bazel git build-essential clang
COPY helloworld /messanger/helloworld
COPY WORKSPACE /messanger/
COPY build.sh /messanger/
COPY fetch.sh /messanger/
WORKDIR /messanger
RUN ls -lh
RUN ./fetch.sh
RUN ./build.sh
RUN ldd /messanger/bazel-bin/helloworld/server

FROM ubuntu:latest
WORKDIR /bin
COPY --from=build /messanger/bazel-bin/helloworld/server /bin

ENTRYPOINT /bin/server
EXPOSE 50051
