FROM  python:3.7
ENV PYTHONUNBUFFERED 1

RUN mkdir /bot
WORKDIR /bot

#RUN  export LC_ALL=C.UTF-8
#RUN  export LANG=C.UTF-8

#RUN apt-get update && apt-get -y install curl

RUN pip3 install --upgrade pip

RUN pip3 install tensorflow-cpu==2.6.1
#RUN pip3 install nltk==3.2.5
#RUN python3 -m nltk.downloader punkt
#RUN python3 -m nltk.downloader stopwords
#RUN python3 -m nltk.downloader perluniprops

ADD . /bot/
RUN pip3 install -r /bot/requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3", "./bot/app/server.py"]
