FROM python:3.11-alpine3.17

ENV PYTHONUNBUFFERED 1

WORKDIR /app/app

RUN apk add nano bash
ENV TZ=Europe/Helsinki

RUN pip install --upgrade pip

COPY app/requirements.txt /app/app/

RUN pip install -r /app/app/requirements.txt

