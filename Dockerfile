FROM python:3.13.1-alpine3.21

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk add nano bash
ENV TZ=Europe/Helsinki

RUN pip install --upgrade pip

COPY app/requirements.txt /app/

RUN pip install -r /app/requirements.txt

