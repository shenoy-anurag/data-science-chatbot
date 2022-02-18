FROM amd64/ubuntu:latest
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.7 python3-pip
RUN python3.7 -m pip install pip
RUN apt-get update && apt-get install -y python3-distutils python3-setuptools
RUN python3.7 -m pip install pip --upgrade pip

RUN mkdir /bot
WORKDIR /bot

RUN export LC_ALL=C.UTF-8
RUN export LANG=C.UTF-8

RUN pip3 install --upgrade pip

RUN pip3 install sanic==21.9.3
RUN pip3 install sanic-cors==1.0.1
RUN pip3 install tensorflow-cpu==2.6.1

ADD . /bot/
RUN chmod +x /bot/bot_entrypoint.sh
RUN pip3 install -r /bot/docker-requirements-x86_64.txt

EXPOSE 8000
