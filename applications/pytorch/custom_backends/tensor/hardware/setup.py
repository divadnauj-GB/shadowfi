import glob
import os
import pathlib
import shutil
import subprocess

from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ROOT = pathlib.Path(__file__).resolve().parent
OBJDIR = ROOT / "obj_dir"
RTL = ROOT / "TCU_core.v"
TOP = "sub_tensor_core"
PREFIX = "Vsub_tensor_core"


def get_verilator_root() -> pathlib.Path:
    env_root = os.environ.get("VERILATOR_ROOT")
    if env_root:
        root = pathlib.Path(env_root).resolve()
        if (root / "include" / "verilated.h").exists():
            return root
        raise RuntimeError(
            f"Invalid VERILATOR_ROOT: {root}\n"
            f"Missing: {root / 'include' / 'verilated.h'}"
        )

    verilator_path = shutil.which("verilator")
    if verilator_path:
        verilator_path = pathlib.Path(verilator_path).resolve()
        candidate = verilator_path.parent.parent / "share" / "verilator"
        if (candidate / "include" / "verilated.h").exists():
            return candidate

    verilator_bin_path = shutil.which("verilator_bin")
    if verilator_bin_path:
        verilator_bin_path = pathlib.Path(verilator_bin_path).resolve()
        candidate = verilator_bin_path.parent.parent / "share" / "verilator"
        if (candidate / "include" / "verilated.h").exists():
            return candidate

    raise RuntimeError(
        "Could not locate Verilator installation.\n"
        "Please either:\n"
        "1) export VERILATOR_ROOT=/path/to/share/verilator\n"
        "2) or make sure `verilator` is available in PATH"
    )


class VerilatedBuildExt(build_ext):
    def run(self):
        verilator_root = get_verilator_root()
        print(f"VERILATOR_ROOT = {verilator_root}")

        OBJDIR.mkdir(exist_ok=True)

        cmd = [
            "verilator",
            "--cc",
            str(RTL),
            "--top-module",
            TOP,
            "--Mdir",
            str(OBJDIR),
            "-O3",
            "--x-assign", "fast",
            "--x-initial", "fast",
            "--no-assert",
            "-Wno-fatal",
            "-Wno-WIDTHTRUNC",
            "-Wno-CASEOVERLAP",
        ]
        subprocess.check_call(cmd)

        generated = sorted(glob.glob(str(OBJDIR / f"{PREFIX}*.cpp")))
        if not generated:
            raise RuntimeError("No Verilator-generated C++ sources were found")

        ext = self.extensions[0]
        ext.sources.extend(generated)

        verilator_include = verilator_root / "include"

        ext.sources.append(str(verilator_include / "verilated.cpp"))

        threads_cpp = verilator_include / "verilated_threads.cpp"
        if threads_cpp.exists():
            ext.sources.append(str(threads_cpp))

        ext.include_dirs.extend(
            [
                str(ROOT / "include"),
                str(OBJDIR),
                str(verilator_include),
                str(verilator_include / "vltstd"),
            ]
        )

        super().run()


ext_modules = [
    Pybind11Extension(
        "tcu_hw",
        [
            "bindings/tcu_hw.cpp",
            "src/tcu_utils.cpp",
            "src/tcu_reference.cpp",
            "src/tcu_driver.cpp",
            "src/tcu_tiled.cpp",
        ],
        include_dirs=[],
        extra_compile_args=[
            "-O3",
            "-std=c++17",
            "-march=native",
            "-flto",
        ],
        extra_link_args=[
            "-flto",
        ],
        cxx_std=17,
    )
]

setup(
    name="tcu-hw",
    version="0.1.0",
    ext_modules=ext_modules,
    cmdclass={"build_ext": VerilatedBuildExt},
    zip_safe=False,
)
