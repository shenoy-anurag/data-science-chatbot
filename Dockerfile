FROM  python:3.7
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

#RUN  export LC_ALL=C.UTF-8
#RUN  export LANG=C.UTF-8

#RUN apt-get update && apt-get -y install curl

RUN pip3 install --upgrade pip

#RUN pip3 install nltk==3.2.5
#RUN python3 -m nltk.downloader punkt
#RUN python3 -m nltk.downloader stopwords
#RUN python3 -m nltk.downloader perluniprops

ADD . /app/
RUN pip3 install -r /app/requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3", "./app/server.py"]
