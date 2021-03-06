#!/bin/sh
APP_NAME="kagayaki"
VERSION="0.1"

WORKDIR=$(pwd)
BUILD=0
EXEC=-1

while getopts v:bxs: flag; do
  case "${flag}" in
    v) VERSION=${OPTARG};;
    b) BUILD=1 && EXEC=0;;
    x) EXEC=1;;
    s) CONTAINER_SAVE=${OPTARG};;
    *) echo "invalid flag ${flag}";;
  esac
done

if [ $BUILD -eq 1 ]; then
  docker build -t ${APP_NAME}:"${VERSION}" .
  if [ -n "${CONTAINER_SAVE+x}" ]; then
    docker save ${APP_NAME}:"${VERSION}" > "$CONTAINER_SAVE"
  fi
fi

if [ $EXEC -eq 1 ] || [ $EXEC -eq -1 ]; then
  docker run -v "${WORKDIR}/db":/db -v "${WORKDIR}/config":/kgyk/config:ro \
  --env-file ./deploy.env -d --name ${APP_NAME} ${APP_NAME}:${VERSION}
fi