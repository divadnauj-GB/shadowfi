# Makefile — build system for the TCU hardware backend
#
# Targets
# -------
#  pybind-install   Install the tcu_hw Python extension (golden + FI models).
#  test-python      Smoke-test that the Python extension loads correctly.
#  test-fi          Run the Python FI testbench (test_fi.py).
#  tb_sim           Build the golden C++ testbench binary (obj_dir/tb_sim).
#  run-tb           Build and execute the golden C++ testbench.
#  tb_fi_sim        Build the FI C++ testbench binary (obj_dir_fi/tb_fi_sim).
#  run-tb-fi        Build and execute the FI C++ testbench.
#  sim-all          Build both C++ testbenches.
#  clean            Remove all generated build artifacts.
#
# Both C++ testbench binaries are placed inside their respective obj_dir/
# directories so they are excluded from version control along with the rest
# of the generated Verilator output.

PYTHON ?= python
CXX    ?= g++

# Auto-detect Verilator binary and root from PATH.
VERILATOR_BIN  := $(shell which verilator 2>/dev/null)
VERILATOR_ROOT := $(shell $(PYTHON) -c \
    'import pathlib; p = pathlib.Path("$(VERILATOR_BIN)").resolve(); \
     print((p.parent.parent / "share" / "verilator").as_posix())' 2>/dev/null)

# Verilator flags shared by both models.
# -Wno-fatal: testbench files in sbtr/ may produce harmless warnings; don't abort.
VFLAGS := -O3 --x-assign fast --x-initial fast --no-assert \
          -Wno-fatal -Wno-WIDTHTRUNC -Wno-CASEOVERLAP

CXXFLAGS := -std=c++17 -O2 \
            -I include \
            -I $(VERILATOR_ROOT)/include \
            -I $(VERILATOR_ROOT)/include/vltstd

# =============================================================================
# Sanity check
# =============================================================================

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

# =============================================================================
# Python extension (golden + FI in a single tcu_hw module)
# =============================================================================

# setup.py handles verilating both models and injecting their generated sources
# into the single tcu_hw extension.  VERILATOR_ROOT is forwarded so setup.py
# finds the runtime headers when building outside of the standard install path.
pybind-install: check-verilator
	$(PYTHON) -m pip install -U pip
	VERILATOR_ROOT=$(VERILATOR_ROOT) $(PYTHON) -m pip install -e .

pyext: check-verilator
	$(PYTHON) -m pip install -U pip
	VERILATOR_ROOT=$(VERILATOR_ROOT) $(PYTHON) -m pip install -e .

test-python: check-verilator
	VERILATOR_ROOT=$(VERILATOR_ROOT) $(PYTHON) -c "import tcu_hw; print(tcu_hw.__doc__)"

test-fi: check-verilator
	VERILATOR_ROOT=$(VERILATOR_ROOT) $(PYTHON) test_fi.py

# =============================================================================
# Golden C++ testbench  (TCU_core.v → obj_dir/ → obj_dir/tb_sim)
# =============================================================================

# Step 1: translate the golden RTL into C++ with Verilator.
obj_dir/Vsub_tensor_core.h: TCU_core.v | check-verilator
	verilator --cc $< --top-module sub_tensor_core --Mdir obj_dir $(VFLAGS)

# Step 2: compile the generated C++ into a static library.
obj_dir/libVsub_tensor_core.a: obj_dir/Vsub_tensor_core.h
	$(MAKE) -C obj_dir -f Vsub_tensor_core.mk CXX=$(CXX) VERILATOR_ROOT=$(VERILATOR_ROOT)

GOLDEN_SRCS := tb_main.cpp \
               src/tcu_driver.cpp \
               src/tcu_reference.cpp \
               src/tcu_tiled.cpp \
               src/tcu_utils.cpp

# Step 3: link the testbench binary inside obj_dir/ so it is not tracked by git.
obj_dir/tb_sim: obj_dir/libVsub_tensor_core.a $(GOLDEN_SRCS)
	$(CXX) $(CXXFLAGS) -I obj_dir \
	    $(GOLDEN_SRCS) \
	    obj_dir/libVsub_tensor_core.a \
	    obj_dir/libverilated.a \
	    -o obj_dir/tb_sim

run-tb: obj_dir/tb_sim
	./obj_dir/tb_sim

tb_sim: obj_dir/tb_sim  # alias

# =============================================================================
# FI C++ testbench  (sbtr/*.v → obj_dir_fi/ → obj_dir_fi/tb_fi_sim)
# =============================================================================

# All .v files in sbtr/ are included so that adding a new instrumented module
# to the folder is immediately picked up without editing this Makefile.
FI_RTL_SRCS := $(wildcard sbtr/*.v)

# --prefix Vsub_tensor_core_fi gives the generated class a different name than
# the golden model (Vsub_tensor_core).  This allows both headers to be included
# in the same translation unit without symbol conflicts.
obj_dir_fi/Vsub_tensor_core_fi.h: $(FI_RTL_SRCS) | check-verilator
	verilator --cc $(FI_RTL_SRCS) --top-module sub_tensor_core \
	    --prefix Vsub_tensor_core_fi --Mdir obj_dir_fi $(VFLAGS)

obj_dir_fi/libVsub_tensor_core_fi.a: obj_dir_fi/Vsub_tensor_core_fi.h
	$(MAKE) -C obj_dir_fi -f Vsub_tensor_core_fi.mk CXX=$(CXX) VERILATOR_ROOT=$(VERILATOR_ROOT)

FI_SRCS := tb_fi_main.cpp \
           src/tcu_fi_driver.cpp \
           src/tcu_fi_types.cpp \
           src/tcu_reference.cpp \
           src/tcu_utils.cpp

obj_dir_fi/tb_fi_sim: obj_dir_fi/libVsub_tensor_core_fi.a $(FI_SRCS)
	$(CXX) $(CXXFLAGS) -I obj_dir_fi \
	    $(FI_SRCS) \
	    obj_dir_fi/libVsub_tensor_core_fi.a \
	    obj_dir_fi/libverilated.a \
	    -o obj_dir_fi/tb_fi_sim

run-tb-fi: obj_dir_fi/tb_fi_sim
	./obj_dir_fi/tb_fi_sim

tb_fi_sim:  obj_dir_fi/tb_fi_sim  # alias
verilate-fi: obj_dir_fi/Vsub_tensor_core_fi.h  # alias

# =============================================================================
# Aggregate and maintenance
# =============================================================================

sim-all: obj_dir/tb_sim obj_dir_fi/tb_fi_sim

clean:
	rm -rf build dist *.egg-info obj_dir obj_dir_fi *.so *.dylib
	rm -rf src/*.egg-info src/*.so
	rm -f tb_sim tb_fi_sim
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

.PHONY: check-verilator pybind-install pyext test-python test-fi \
        run-tb run-tb-fi tb_sim tb_fi_sim verilate-fi sim-all clean
