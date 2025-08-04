FROM python:3.10.14-bullseye as base 

RUN apt-get update && \
  apt-get install -y \
  locales \
  locales-all && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN groupadd -g 900 mesop && useradd -u 900 -s /bin/bash -g mesop mesop
USER mesop

COPY . /srv/mesop-app
WORKDIR /srv/mesop-app

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "src.main:me"]