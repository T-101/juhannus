FROM python:3.7-alpine3.9

ENV PYTHONUNBUFFERED 1

RUN mkdir /juhannus

WORKDIR /juhannus/app/

RUN apk add nano tzdata
RUN cp /usr/share/zoneinfo/Europe/Helsinki /etc/localtime
RUN echo "Europe/Helsinki" > /etc/timezone

ADD app/requirements.txt /juhannus/app/

RUN pip install -r requirements.txt

ADD . /juhannus/

EXPOSE 8000

# COPY entry.sh /entry.sh

# CMD ['/entry.sh']

CMD gunicorn config.wsgi --timeout 600 -w 4 -b 0.0.0.0:8000
