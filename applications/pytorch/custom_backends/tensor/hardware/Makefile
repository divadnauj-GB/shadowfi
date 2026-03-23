PYTHON ?= python

VERILATOR_BIN  := $(shell which verilator 2>/dev/null)
VERILATOR_ROOT := $(shell $(PYTHON) -c 'import pathlib; p = pathlib.Path("$(VERILATOR_BIN)").resolve(); print((p.parent.parent / "share" / "verilator").as_posix())' 2>/dev/null)

check-verilator:
	@if [ -z "$(VERILATOR_BIN)" ]; then \
		echo "Error: verilator is not in PATH"; \
		exit 1; \
	fi
	@if [ ! -f "$(VERILATOR_ROOT)/include/verilated.h" ]; then \
		echo "Error: detected VERILATOR_ROOT is invalid: $(VERILATOR_ROOT)"; \
		exit 1; \
	fi
	@echo "Using verilator: $(VERILATOR_BIN)"
	@echo "Detected VERILATOR_ROOT: $(VERILATOR_ROOT)"

pybind-install: check-verilator
	$(PYTHON) -m pip install -U pip
	VERILATOR_ROOT=$(VERILATOR_ROOT) $(PYTHON) -m pip install -e .

pyext: check-verilator
	$(PYTHON) -m pip install -U pip
	VERILATOR_ROOT=$(VERILATOR_ROOT) $(PYTHON) -m pip install -e .

test-python: check-verilator
	VERILATOR_ROOT=$(VERILATOR_ROOT) $(PYTHON) -c "import tcu_hw; print(tcu_hw.__doc__)"

clean:
	rm -rf build dist *.egg-info obj_dir *.so *.dylib
	rm -rf src/*.egg-info src/*.so
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

.PHONY: check-verilator pybind-install pyext test-python clean
