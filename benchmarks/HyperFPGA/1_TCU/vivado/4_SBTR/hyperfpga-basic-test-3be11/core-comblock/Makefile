#!/usr/bin/make

PANOPT = -V geometry:margin=2cm -V papersize:a4

.PHONY: doc

all: doc test metrics

doc:
	cd doc; pandoc $(PANOPT) -o ../src/comblock/doc/user_guide.pdf user_guide.md

test:
	make -C testbench

metrics:
	make -C examples/measurements

clean:
	make -C testbench clean
	make -C examples/measurements clean
