# TCU Custom Backend for PyTorch

Custom PyTorch backend that routes `nn.Linear` and `nn.Conv2d` operations through a cycle-accurate hardware simulation of a Tensor Core Unit (TCU). Supports both golden execution and hardware fault injection, making it possible to study the effect of hardware faults on neural network inference without physical hardware.

---

## Architecture

The project is organized as a vertical stack, each layer building on the one below.

```
PyTorch model (nn.Linear / nn.Conv2d)
        │
RTLLinearWrapper / RTLConv2dWrapper     ← nn.Module, handles quantization and format
        │
TensorBackend                            ← selects golden or FI path, manages the core
        │
tcu_hw  (Python extension, pybind11)     ← TcuHardware | TcuFiHardware | FaultConfig
        │
TcuDriver / TcuFiDriver  (C++)           ← clock/reset, matrix load/read, SR protocol
        │
Vsub_tensor_core / Vsub_tensor_core_fi   ← Verilated C++ models
        │
TCU_core.v / sub_tensor_core_fi_sbtr.v   ← Verilog RTL
```

### RTL

`hardware/TCU_core.v` — synthesized by Yosys from a high-level description. Top module `sub_tensor_core` contains a 4×4 grid of `dot_unit_core` instances. Each `dot_unit_core` computes one element of the output tile:

```
W[i][j] = A[i][0]*B[0][j] + A[i][1]*B[1][j] + A[i][2]*B[2][j] + A[i][3]*B[3][j] + C[i][j]
```

The pipeline uses 3-stage pipelined floating-point multipliers (`fpmult_3_pipe`) and adders (`fpadd_3_pipe`), giving a total latency of **12 clock cycles** per tile.

`hardware/sbtr/sub_tensor_core_fi_sbtr.v` — the same RTL with saboteur cells inserted inside `adder0` of `d_unit0` (the dot unit that produces `W[0][0]`). Saboteurs are controlled via a 1534-bit shift register and a trigger signal.

### Hardware simulation

Verilator translates the RTL to C++. Two models are compiled:

| Model | Prefix | Header | Purpose |
|---|---|---|---|
| Golden | `Vsub_tensor_core` | `obj_dir/Vsub_tensor_core.h` | Clean execution, no fault |
| FI | `Vsub_tensor_core_fi` | `obj_dir_fi/Vsub_tensor_core_fi.h` | Fault injection via saboteurs |

Different prefixes allow both classes to coexist in the same shared library.

### Python extension — `tcu_hw`

A single pybind11 shared library exposing both models under one module. See [Python API](#python-api) below.

---

## Repository structure

```
tensor/
├── Backend.py              # TensorBackend: golden/FI dispatch, runtime fault control
├── RTLLinearWrapper.py     # nn.Module wrapping nn.Linear  (float and int8 modes)
├── RTLConv2dWrapper.py     # nn.Module wrapping nn.Conv2d  (im2col → GEMM)
├── utils.py                # Symmetric quantization helpers
├── __init__.py             # Exports wrapper dict {linear, conv2d}
└── hardware/
    ├── TCU_core.v              # Golden RTL (Yosys-synthesized)
    ├── sbtr/                   # FI-instrumented RTL and testbench files
    │   ├── sub_tensor_core_fi_sbtr.v
    │   ├── fpadd_3_pipe_gate_sbtr.v
    │   ├── basic_sabotuer.v
    │   ├── super_sabouter.v
    │   ├── shift_register.v
    │   └── ...
    ├── include/                # C++ headers
    │   ├── tcu_types.hpp       # vec4f, mat4f
    │   ├── tcu_driver.hpp      # TcuDriver (golden)
    │   ├── tcu_fi_types.hpp    # FiHwParams, FaultConfig, FaultMode
    │   ├── tcu_fi_driver.hpp   # TcuFiDriver (FI)
    │   ├── tcu_matrix.hpp      # Dynamic Matrixf class
    │   ├── tcu_reference.hpp   # Software reference GEMM
    │   ├── tcu_tiled.hpp       # Tiled GEMM engine
    │   └── tcu_utils.hpp       # Float ↔ uint32, pack/unpack helpers
    ├── src/                    # C++ implementations
    ├── bindings/tcu_hw.cpp     # pybind11 module (golden + FI in one)
    ├── tb_main.cpp             # C++ testbench — golden path
    ├── tb_fi_main.cpp          # C++ testbench — fault injection
    ├── test.py                 # Python testbench — golden path
    ├── test_fi.py              # Python testbench — fault injection
    ├── setup.py                # Build system (verilates both models)
    ├── pyproject.toml          # Package metadata
    └── Makefile                # C++ testbench targets
```

---

## Requirements

- Python ≥ 3.9, NumPy, PyTorch
- Verilator ≥ 5.x (in PATH or via `VERILATOR_ROOT`)
- pybind11 ≥ 3.0
- C++17 compiler (clang++ or g++)

---

## Installation

```bash
cd hardware/

# Install into the active Python environment
make pybind-install

# Or directly with pip (pass Verilator root if not in PATH)
VERILATOR_ROOT=/path/to/share/verilator pip install -e .
```

This verilates both the golden and FI models, compiles the pybind11 extension, and installs `tcu_hw` into the environment.

To install into a specific conda environment:

```bash
VERILATOR_ROOT=$(python -c 'import pathlib,shutil; p=pathlib.Path(shutil.which("verilator")).resolve(); print((p.parent.parent/"share"/"verilator").as_posix())') \
conda run -n SHADOWFI pip install -e hardware/
```

---

## Python API

### `tcu_hw` module

```python
import tcu_hw

# Software reference (no simulation)
result = tcu_hw.matmul_ref(A, B, C)

# Stateless golden hardware run
result = tcu_hw.matmul_hw(A, B, C, tile_latency=12)

# Stateless FI hardware run
cfg    = tcu_hw.FaultConfig(tcu_hw.FaultMode.STUCK_AT_0, [1500, 1501], fault_cycle=6)
result = tcu_hw.matmul_fi_hw(A, B, C, cfg)

# target_nodes acepta cualquier lista de enteros
cfg = tcu_hw.FaultConfig(tcu_hw.FaultMode.STUCK_AT_0, list(range(1500, 1532)))

# Persistent golden core (reused across calls)
hw     = tcu_hw.TcuHardware(tile_latency=12)
result = hw.matmul(A, B, C)

# Persistent FI core
fi_hw  = tcu_hw.TcuFiHardware(sr_length=1534, tile_latency=12)
result = fi_hw.matmul(A, B, C)           # golden path through FI model
result = fi_hw.matmul_fi(A, B, C, cfg)  # automated FI per tile

# Manual FI control
fi_hw.fi_configure(cfg)   # load shift register
fi_hw.fi_arm()            # assert TFEn — fault becomes active
result = fi_hw.matmul(A, B, C)
fi_hw.fi_disarm()         # deassert TFEn
```

#### `FaultConfig`

| Field | Type | Description |
|---|---|---|
| `mode` | `FaultMode` | `STUCK_AT_0`, `STUCK_AT_1`, or `BIT_FLIP` |
| `target_nodes` | `list[int]` | Saboteur indices to arm (0 – 1531 for current RTL) |
| `fault_cycle` | `int` | Pipeline cycle for TFEn pulse (`BIT_FLIP` only, range 1–12) |

#### Fault modes

| Mode | Behavior |
|---|---|
| `STUCK_AT_0` | Forces targeted nodes to 0 for the entire tile execution |
| `STUCK_AT_1` | Forces targeted nodes to 1 for the entire tile execution |
| `BIT_FLIP` | Inverts targeted nodes for exactly one clock cycle at `fault_cycle` |

---

### `TensorBackend`

Central dispatcher used by the layer wrappers.

```python
from tensor.Backend import TensorBackend
import tcu_hw

# Golden mode (default)
backend = TensorBackend(format="float")

# FI mode — pass a FaultConfig at construction
cfg     = tcu_hw.FaultConfig(tcu_hw.FaultMode.STUCK_AT_0, [1500, 1501, 1502])
backend = TensorBackend(format="float", fault_config=cfg)

# Switch modes at runtime
backend.set_fault_config(cfg)    # enable FI  (rebuilds core if needed)
backend.clear_fault()            # disable FI (rebuilds core back to golden)

result = backend.matmul(A, B, C)
```

| Parameter | Default | Description |
|---|---|---|
| `format` | `"float"` | `"float"` → hardware sim; `"int"` → NumPy integer path |
| `bitwidth` | `8` | Quantization bits (int mode only) |
| `tile_latency` | `12` | Clock cycles per 4×4 tile |
| `persistent_core` | `True` | Reuse hardware instance across calls |
| `fault_config` | `None` | Active `FaultConfig`, or `None` for golden mode |
| `sr_length` | `1534` | Shift register length of the FI RTL variant |

**Note:** `format="int"` always uses a NumPy fallback regardless of `fault_config`. The hardware FI model operates on float32 only.

---

### Layer wrappers

```python
from tensor import RTLLinearWrapper, RTLConv2dWrapper
import torch.nn as nn

# Replace an existing Linear layer
linear = nn.Linear(128, 64)
rtl_linear = RTLLinearWrapper(linear, format="float")

# Replace an existing Conv2d layer
conv = nn.Conv2d(32, 64, kernel_size=3, padding=1)
rtl_conv = RTLConv2dWrapper(conv, format="float")
```

`RTLConv2dWrapper` uses the **im2col** strategy: `F.unfold` extracts sliding patches into a 2D matrix, which is then passed to `TensorBackend.matmul` as a standard GEMM.

The wrappers currently **do not** forward `fault_config` to `TensorBackend`. To run a layer with fault injection active, set the fault on the backend directly after construction or subclass the wrapper.

---

## Testing

```bash
cd hardware/

# C++ golden testbench (9×10 @ 10×11, tolerance 1e-4)
make run-tb

# C++ FI testbench (8 test cases across all fault modes)
make run-tb-fi

# Python golden testbench
python test.py

# Python FI testbench
python test_fi.py
```

---

## Fault injection scope and current limitations

### What is currently instrumented

Only **`adder0` of `d_unit0`** inside `sub_tensor_core` is FI-instrumented. This is the first partial-sum adder in the dot unit that produces **`W[0][0]`** (row 0, column 0 of each 4×4 output tile). The remaining 15 dot units compute normally.

| Coverage | Status |
|---|---|
| `W[0][0]` element of each tile | Instrumented — 1532 addressable saboteur nodes |
| `W[0][1]` through `W[3][3]` | Not instrumented — always computed correctly |
| Integer format (`format="int"`) | Not instrumented — NumPy path, no hardware involved |
| Attention layers | Not yet wrapped |

### Masked faults

A fault is **masked** when the targeted node naturally holds the same value the fault would force (e.g. STUCK_AT_0 on a node that is already 0). Masked faults produce no observable error. Observability depends on the specific inputs and which pipeline stage is targeted.

### Tile size

The hardware tile size is fixed at **4×4**. The tiled GEMM engine pads inputs to the next multiple of 4 and crops the output back to the original shape. Non-multiple-of-4 matrices are handled transparently.

### Precision

The hardware operates on **IEEE 754 float32**. Results differ from software float32 by up to ~1×10⁻⁶ due to pipeline register rounding and partial-sum accumulation order. This is not a fault — it is the expected behavior of the hardware pipeline.
