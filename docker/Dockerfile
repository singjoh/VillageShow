FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
ADD requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt
COPY src/*.py /app
COPY sql/*.sql /app/sql/
COPY resources/* /app/resources/
EXPOSE 8080
# CMD ["python", "-u", "app.py"]
