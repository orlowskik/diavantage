FROM python:3.11
LABEL authors="Kamil"

WORKDIR /usr/src/diavantage

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY "django-insecure-!%l!^h!x!l^q!h^#q4^!w5*^x=5%_n^i!z7!qk+!@8m^+!k5"
ENV ALLOWED_HOSTS "localhost 127.0.0.1"

RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


