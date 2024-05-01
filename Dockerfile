FROM python:3.11.6-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc python3-dev

WORKDIR /app

COPY requirements/prod.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
  && pip install --no-cache-dir --upgrade -r prod.txt

RUN rm -rf /var/lib/apt/lists/*

COPY src .