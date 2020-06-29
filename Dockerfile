FROM python:3

RUN apt update -y 
RUN apt upgrade -y

COPY . /varylatex

RUN apt install texlive-full -y
RUN apt install graphviz -y

WORKDIR /varylatex
RUN pip install -r requirements.txt
