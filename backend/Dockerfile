FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/

COPY . .

RUN rm -f .env

CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}
