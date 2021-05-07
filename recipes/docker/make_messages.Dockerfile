FROM python:3.9

ADD ./messages ./messages

RUN apt-get update
RUN apt-get install -y protobuf-compiler
WORKDIR "/messages"
RUN pip install -r requirements.txt

RUN make messages
