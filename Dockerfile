FROM python:3.7.4-alpine
LABEL maintainer="sjquant (seonujang92@gmail.com)"

RUN apk add --no-cache bash && apk --no-cache add tzdata && \
        cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
        echo "Asia/Seoul" > /etc/timezone && \
        apk add --no-cache libpq postgresql-dev && \
        apk add --no-cache  build-base

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app