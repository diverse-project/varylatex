#!/bin/sh
set -e

latexFileName="VaryingVariability-FSE15-demo"

PDFLATEX="pdflatex -interaction=nonstopmode -synctex=1 -file-line-error"
FILTER="grep -v -e /usr/share/texlive"

$PDFLATEX $latexFileName | $FILTER && printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -
bibtex $latexFileName && printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -
$PDFLATEX $latexFileName | $FILTER && printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -
$PDFLATEX $latexFileName | $FILTER
open -a Preview $latexFileName".pdf"



