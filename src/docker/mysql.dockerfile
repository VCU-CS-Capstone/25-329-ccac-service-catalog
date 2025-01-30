# Dockerfile used to create a MySQL docker image given the desired Architecture, Platform and Tag
# You can find the necessary argument values at https://hub.docker.com/_/mysql
# ex: docker build --build-arg ARCHITECTURE=arm64/v8 --tag ccac/mysql -f mysql.dockerfile .

ARG ARCHITECTURE="amd64"
ARG PLATFORM="linux"
ARG TAG="8.0"

FROM --platform=${PLATFORM}/${ARCHITECTURE} mysql:${TAG}
