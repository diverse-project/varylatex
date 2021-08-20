#\bin\sh
wget -O mupdf.tar.gz https://mupdf.com/downloads/archive/mupdf-1.18.0-source.tar.gz ;
tar -xzf mupdf.tar.gz
ls
cd mupdf-1.18.0-source
make
make HAVE_X11=no HAVE_GLUT=no prefix=/usr/local install
