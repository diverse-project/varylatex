FROM python:3

RUN apt-get update -y\
 && apt-get install texlive-full -y\
 && apt-get install graphviz -y\
 && rm -rf /var/lib/apt/lists/*


COPY . /varylatex
WORKDIR /varylatex

RUN pip install -r requirements.txt

VOLUME /varylatex/build

CMD /bin/bash
