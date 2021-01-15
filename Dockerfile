FROM ubuntu

RUN useradd -ms /bin/bash safeapp
WORKDIR /home/safeapp

RUN apt-get update -y
RUN apt-get install -y python3
RUN apt-get install -y python3-venv

COPY requirements.txt requirements.txt
RUN python3 -m venv venv
RUN venv/bin/pip install wheel
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY safeapp.py config.py boot.sh ./
COPY certs certs
RUN chmod +x boot.sh

ENV FLASK_APP safeapp.py
RUN chown -R safeapp:safeapp ./
USER safeapp

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]