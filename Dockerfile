FROM python:3.8.1
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /src/
EXPOSE 8000