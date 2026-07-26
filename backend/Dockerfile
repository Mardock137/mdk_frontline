# syntax=docker/dockerfile:1

FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Le dipendenze si copiano e installano prima del resto del codice,
# cosi' Docker riusa questo layer nelle build successive se requirements.txt non cambia.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Cloud Run inietta la porta reale tramite la variabile PORT (default 8080).
EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
