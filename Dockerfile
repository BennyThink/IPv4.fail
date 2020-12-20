FROM python:alpine

WORKDIR /APP
RUN  apk update && apk add git && \
git clone https://github.com/BennyThink/IPv4.fail /APP && pip install -r requirements

CMD python main.py