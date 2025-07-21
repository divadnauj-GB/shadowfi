#!/usr/bin/make
# by RAM

TARGET=workshop.pdf

%.pdf: %.tex
	pdflatex $<
	pdflatex $<
	@rm -fr *.log *.tdo *.out *.aux .*.ini *.snm *.toc *.nav *.vrb

all: $(TARGET)

clean:
	@rm -fr *.log *.tdo *.out *.aux .*.ini *.snm *.toc *.nav *.vrb $(TARGET)

