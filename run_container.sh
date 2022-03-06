#!/bin/sh
APP_NAME="kagayaki"
VERSION="0.1"

WORKDIR=$(pwd)

docker build -t ${APP_NAME}:${VERSION} .

docker run -v "${WORKDIR}/db":/db -v "${WORKDIR}/config":/kgyk/config:ro \
--env-file ./deploy.env -d --name ${APP_NAME} ${APP_NAME}:${VERSION}