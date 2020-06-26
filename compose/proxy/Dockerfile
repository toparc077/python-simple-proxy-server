FROM python:3.8-alpine

RUN apk update && apk add --no-cache --virtual \
    build-deps gcc python3-dev musl-dev libffi-dev py-cryptography openssl-dev

COPY compose/proxy/start-proxy /start-proxy

RUN sed -i 's/\r//' /start-proxy && chmod +x /start-proxy 
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

EXPOSE 8080
ENTRYPOINT ["/start-proxy"]
