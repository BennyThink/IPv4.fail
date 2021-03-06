FROM python:alpine

WORKDIR /APP
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt && rm /requirements.txt
COPY . /APP

CMD ["python", "main.py","-h=", "0.0.0.0"]
