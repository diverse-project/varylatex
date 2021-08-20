FROM python:3.9.6-bullseye

#Update the image we start from and install all latex stuf and dependencies for mupdf
RUN apt-get update -y\
 && apt-get install texlive-full -y\
 && apt-get install graphviz -y\
 && apt-get install libx11-dev mesa-common-dev libgl1-mesa-dev -y\
 && rm -rf /var/lib/apt/lists/*

#Copy varylatex files to the image
COPY . /varylatex
WORKDIR /varylatex

#Install mupdf 1.18.16 version
RUN sh mupdf_install.sh

#Install varylatex python dependencies
RUN pip install -r requirements.txt

VOLUME /varylatex/build

CMD /bin/bash
