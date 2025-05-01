FROM python:latest
WORKDIR /app
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY src/*.py /app
COPY sql/*.sql /app/sql/
COPY resources/* /app/resources/
EXPOSE 8080
# CMD ["python", "-u", "app.py"]
