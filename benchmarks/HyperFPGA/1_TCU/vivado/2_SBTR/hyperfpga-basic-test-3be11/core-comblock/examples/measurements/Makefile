#!/usr/bin/make

all: utilization.md

build/utilization.rpt:
	python3 implement.py

utilization.md: build/utilization.rpt
	@grep -i " Instance "         $< >  $@
	@echo "|-|-|-|-|-|-|-|-|-|-|"    >> $@
	@grep -i " comblock_full "    $< >> $@
	@grep -i " comblock_fifos "   $< >> $@
	@grep -i " comblock_dram "    $< >> $@
	@grep -i " comblock_regs16 "  $< >> $@
	@grep -i " comblock_regs4 "   $< >> $@
	@sed  -i 's/ //g'                   $@

clean:
	@rm -fr build
