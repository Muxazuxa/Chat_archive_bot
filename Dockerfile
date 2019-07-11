FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /telebot
WORKDIR /telebot
ADD . /telebot/
RUN pip3 install -r requirements.txt