FROM python:3.9-slim-buster as builder

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove --purge -y gcc libpq-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

FROM python:3.9-slim-buster

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

ENV FLASK_ENV=production
ENV PORT=5000

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]