FROM python:3.6-alpine3.11

RUN adduser -D safeapp

WORKDIR /home/safeapp

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev
RUN pip install cryptography==3.3.1
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY safeapp.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP safeapp.py
RUN chown -R safeapp:safeapp ./
USER safeapp

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]