"""
setup.py — builds the 'tcu_hw' pybind11 extension.

The extension contains two Verilated models compiled into one shared library:

  Golden model  (obj_dir/)     Vsub_tensor_core
  FI model      (obj_dir_fi/)  Vsub_tensor_core_fi

Using a different --prefix for the FI model prevents the two generated C++
classes from having the same name and colliding at link time.

Both models expose the same top-level RTL ports (A/B/C inputs, W output) but
the FI model adds i_FI_CONTROL_PORT and i_SI for shift-register-based fault
injection.

FI RTL sources are discovered automatically from sbtr/*.v so that adding a new
instrumented file to the folder is sufficient to include it in the build without
editing this script.

verilated.cpp (the Verilator runtime) is added to the extension only once, when
processing the golden model.  Adding it again for the FI model would produce
duplicate symbol errors at link time.
"""

import glob
import os
import pathlib
import shutil
import subprocess

from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ROOT  = pathlib.Path(__file__).resolve().parent
TOP   = "sub_tensor_core"  # Verilog top module name, same for both RTL variants

# --- Golden model ---
OBJDIR_GOLDEN = ROOT / "obj_dir"
RTL_GOLDEN    = ROOT / "TCU_core.v"
PREFIX_GOLDEN = "Vsub_tensor_core"        # Verilated C++ class name

# --- FI model ---
# sbtr/*.v is discovered at build time; no hardcoded file list needed.
OBJDIR_FI = ROOT / "obj_dir_fi"
PREFIX_FI = "Vsub_tensor_core_fi"         # distinct prefix avoids linker conflicts

# Verilator flags shared by both models.
# -Wno-fatal prevents warnings from testbench files in sbtr/ from aborting the build.
VFLAGS = [
    "-O3",
    "--x-assign", "fast",
    "--x-initial", "fast",
    "--no-assert",
    "-Wno-fatal",
    "-Wno-WIDTHTRUNC",
    "-Wno-CASEOVERLAP",
]

CXX_FLAGS  = ["-O3", "-std=c++17", "-march=native", "-flto"]
LINK_FLAGS = ["-flto"]


def get_verilator_root() -> pathlib.Path:
    """Locate the Verilator installation directory.

    Checks VERILATOR_ROOT first, then searches PATH for 'verilator' or
    'verilator_bin' and derives the root from the binary location.
    """
    env_root = os.environ.get("VERILATOR_ROOT")
    if env_root:
        root = pathlib.Path(env_root).resolve()
        if (root / "include" / "verilated.h").exists():
            return root
        raise RuntimeError(
            f"Invalid VERILATOR_ROOT: {root}\n"
            f"Missing: {root / 'include' / 'verilated.h'}"
        )
    for binary in ("verilator", "verilator_bin"):
        path = shutil.which(binary)
        if path:
            candidate = pathlib.Path(path).resolve().parent.parent / "share" / "verilator"
            if (candidate / "include" / "verilated.h").exists():
                return candidate
    raise RuntimeError(
        "Could not locate Verilator installation.\n"
        "Set VERILATOR_ROOT or ensure 'verilator' is in PATH."
    )


def run_verilator(rtl_files: list, objdir: pathlib.Path, prefix: str) -> None:
    """Run Verilator in --cc mode to generate C++ from one or more RTL files."""
    objdir.mkdir(exist_ok=True)
    cmd = (
        ["verilator", "--cc"]
        + [str(f) for f in rtl_files]
        + ["--top-module", TOP, "--prefix", prefix, "--Mdir", str(objdir)]
        + VFLAGS
    )
    subprocess.check_call(cmd)


def inject_verilated_sources(
    ext: Pybind11Extension,
    objdir: pathlib.Path,
    prefix: str,
    verilator_root: pathlib.Path,
    *,
    add_runtime: bool,
) -> None:
    """Append Verilator-generated sources and include paths to a pybind11 extension.

    add_runtime controls whether verilated.cpp (and verilated_threads.cpp) are
    also added.  These runtime files must appear exactly once in the final link,
    so pass add_runtime=True for the first model and add_runtime=False for any
    subsequent model compiled into the same extension.
    """
    generated = sorted(glob.glob(str(objdir / f"{prefix}*.cpp")))
    if not generated:
        raise RuntimeError(f"No Verilator-generated C++ sources found in {objdir}")

    ext.sources.extend(generated)

    verilator_include = verilator_root / "include"

    if add_runtime:
        ext.sources.append(str(verilator_include / "verilated.cpp"))
        threads_cpp = verilator_include / "verilated_threads.cpp"
        if threads_cpp.exists():
            ext.sources.append(str(threads_cpp))

    # Each objdir needs to be on the include path so the generated headers
    # (e.g. Vsub_tensor_core.h and Vsub_tensor_core_fi.h) are found.
    ext.include_dirs.extend([
        str(ROOT / "include"),
        str(objdir),
        str(verilator_include),
        str(verilator_include / "vltstd"),
    ])


class VerilatedBuildExt(build_ext):
    def run(self):
        verilator_root = get_verilator_root()
        print(f"VERILATOR_ROOT = {verilator_root}")

        ext = next(e for e in self.extensions if e.name == "tcu_hw")

        # Step 1: verilate the golden model and inject its sources.
        # add_runtime=True so verilated.cpp is included exactly once.
        run_verilator([RTL_GOLDEN], OBJDIR_GOLDEN, PREFIX_GOLDEN)
        inject_verilated_sources(ext, OBJDIR_GOLDEN, PREFIX_GOLDEN, verilator_root,
                                 add_runtime=True)

        # Step 2: discover all .v files in sbtr/ and verilate the FI model.
        # Testbench files (new_tb_tcu.v, tb_sbtr_cntrl.v) are included but
        # their modules are not reachable from --top-module sub_tensor_core so
        # Verilator ignores them during elaboration.
        fi_rtl_srcs = sorted((ROOT / "sbtr").glob("*.v"))
        print(f"FI RTL sources ({len(fi_rtl_srcs)} files):")
        for f in fi_rtl_srcs:
            print(f"  {f.name}")

        run_verilator(fi_rtl_srcs, OBJDIR_FI, PREFIX_FI)
        inject_verilated_sources(ext, OBJDIR_FI, PREFIX_FI, verilator_root,
                                 add_runtime=False)  # runtime already added above

        super().run()


ext_modules = [
    Pybind11Extension(
        "tcu_hw",
        sources=[
            # Python binding (golden + FI logic in one module)
            "bindings/tcu_hw.cpp",
            # Golden model C++ driver and helpers
            "src/tcu_utils.cpp",
            "src/tcu_reference.cpp",
            "src/tcu_driver.cpp",
            "src/tcu_tiled.cpp",
            # FI model C++ driver and helpers
            "src/tcu_fi_types.cpp",
            "src/tcu_fi_driver.cpp",
            # Verilator-generated sources are appended dynamically by
            # VerilatedBuildExt.run() above (obj_dir/*.cpp + obj_dir_fi/*.cpp).
        ],
        include_dirs=[],   # populated dynamically by inject_verilated_sources
        extra_compile_args=CXX_FLAGS,
        extra_link_args=LINK_FLAGS,
        cxx_std=17,
    ),
]

setup(
    name="tcu-hw",
    version="0.1.0",
    ext_modules=ext_modules,
    cmdclass={"build_ext": VerilatedBuildExt},
    zip_safe=False,
)
