FROM python:3.9

ADD ./tests ./tests
ADD ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt
