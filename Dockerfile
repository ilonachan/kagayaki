# Use a builder container to install the dependencies,
# then switch to a more lightweight interpreter
FROM python:3.10-alpine3.15

COPY requirements.txt .
RUN apk update
RUN apk add --update --no-cache --virtual .build-deps alpine-sdk python3-dev
RUN pip install --user -r requirements.txt

WORKDIR /kgyk

VOLUME /kgyk/config

# default database volume in case nothing usable is provided
VOLUME /db
# and default env variables pointing there
ENV DB_LOCATION sqlite:////db/kagayaki.sqlite
ENV DB_PLAYGROUND_LOCATION sqlite:////db/playground.sqlite

# This will become relevant if I add a web interface to my bot
# ENV SERVER_PORT 8080
# EXPOSE $SERVER_PORT

COPY ./logging.yaml .

# copy the code and default configuration
COPY ./kagayaki ./kagayaki

CMD [ "python", "-m", "kagayaki" ]