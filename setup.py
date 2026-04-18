"""
setup.py — Invokes CMake to build the C++ extension and install it as a Python package.
"""

import os
import subprocess
import sys
from pathlib import Path

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    """A setuptools Extension that delegates to CMake."""

    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[])
        self.sourcedir = str(Path(sourcedir).resolve())


class CMakeBuild(build_ext):
    """Custom build_ext that runs CMake configure → build → install."""

    def build_extension(self, ext: CMakeExtension) -> None:
        ext_path = Path(self.get_ext_fullpath(ext.name))
        install_dir = ext_path.parent.resolve()

        cmake_executable = os.environ.get("CMAKE", "cmake")
        build_type = os.environ.get("CMAKE_BUILD_TYPE", "Release")

        cc = os.environ.get("CC", "clang")
        cxx = os.environ.get("CXX", "clang++")

        build_dir = Path(self.build_temp)
        build_dir.mkdir(parents=True, exist_ok=True)

        configure_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={install_dir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={build_type}",
            f"-DCMAKE_C_COMPILER={cc}",
            f"-DCMAKE_CXX_COMPILER={cxx}",
            "-G", "Ninja" if self._has_ninja() else "Unix Makefiles",
        ]

        subprocess.check_call(
            [cmake_executable, "-S", ext.sourcedir, "-B", str(build_dir)]
            + configure_args
        )

        subprocess.check_call(
            [cmake_executable, "--build", str(build_dir), "--config", build_type]
        )

    @staticmethod
    def _has_ninja() -> bool:
        try:
            subprocess.run(["ninja", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


setup(
    ext_modules=[CMakeExtension("mylib._core", sourcedir=".")],
    cmdclass={"build_ext": CMakeBuild},
    package_dir={"mylib": "src/python/mylib"},
    packages=["mylib"],
)
