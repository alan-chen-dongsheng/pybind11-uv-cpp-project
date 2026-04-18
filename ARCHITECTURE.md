# Architecture Document

> pybind11-uv-cpp-project — High-Performance C++ Extension for Python

---

## 1. Project Overview

This project demonstrates how to write core business logic in **C++**, expose it to Python via **pybind11**, and package it as a standard Python module that users install with a single `uv pip install` command — no manual compilation, no Makefiles, no `cmake` invocations from the user side.

### Key Design Goals

| Goal | Solution |
|------|----------|
| Python-friendly installation | `uv pip install -e "."` triggers everything |
| C++ performance | Clang + `-O3 -march=native` |
| Clean separation | C++ core has zero Python dependency |
| Reproducible builds | Build isolation via uv/setuptools |

---

## 2. Directory Layout

```
├── pyproject.toml          ← Python package metadata & build deps
├── setup.py                ← The bridge: setuptools → CMake
├── CMakeLists.txt          ← Top-level CMake config (compilers, standards)
├── MANIFEST.in             ← Source distribution file list
├── .gitignore              ← Build artifacts exclusion
│
├── src/
│   ├── cpp/
│   │   ├── core/           ← Pure C++ (no Python, no pybind11)
│   │   │   ├── CMakeLists.txt
│   │   │   ├── calculator.hpp
│   │   │   └── calculator.cpp
│   │   └── bindings/       ← pybind11 glue layer
│   │       ├── CMakeLists.txt
│   │       └── main.cpp
│   └── python/
│       └── mylib/
│           └── __init__.py ← Python package entry point
│
├── tests/
│   └── test_calculator.py  ← pytest test suite
│
└── examples/
    └── basic_usage.py      ← Usage demo
```

### Directory Responsibilities

| Directory | Owns | May Depend On | Must NOT Depend On |
|-----------|------|---------------|---------------------|
| `src/cpp/core/` | Business logic C++ classes/functions | Standard library only | Python, pybind11 |
| `src/cpp/bindings/` | Python-C++ bridge | core, pybind11, Python C API | Nothing else |
| `src/python/mylib/` | Python package entry, pure-Python wrappers | C++ extension (`_core`) | C++ internals |

This **three-layer architecture** ensures:
1. C++ core can be compiled and used standalone (in other C++ projects)
2. Bindings layer can be swapped (e.g., to Cython, nanobind) without touching core
3. Python layer stays thin — just re-exports

### MANIFEST.in — Source Distribution

```
include pyproject.toml
include CMakeLists.txt
recursive-include src *.hpp *.cpp *.py CMakeLists.txt
recursive-include tests *.py
```

`MANIFEST.in` ensures that when you build a source distribution (`sdist`), all C++ source files, CMake configs, and Python files are included. Without it, `sdist` would only package Python files by default, and users downloading the source tarball couldn't compile the C++ extension.

---

## 3. How C++ Exposes Itself to Python

### 3.1 pybind11 Binding Mechanism

The magic happens in `src/cpp/bindings/main.cpp`:

```cpp
PYBIND11_MODULE(_core, m) {
    m.doc() = "High-performance C++ calculator module";

    py::class_<mylib::Calculator>(m, "Calculator")
        .def(py::init<>())
        .def(py::init<double>(), py::arg("initial_value"))
        .def("add", &mylib::Calculator::add, py::arg("value"))
        // ... more bindings

    m.def("power", &mylib::power, py::arg("base"), py::arg("exponent"));
}
```

`PYBIND11_MODULE(_core, m)` is a macro that generates a Python C extension module entry point. When Python imports `mylib._core`, it loads the compiled shared object (`.so`) and calls this initialization function.

The `_core` module name becomes `_core.cpython-312-x86_64-linux-gnu.so` after compilation — the suffix encodes the Python ABI and platform.

### 3.2 Type Mapping

pybind11 automatically converts between C++ and Python types:

| C++ Type | Python Type | Mechanism |
|----------|-------------|-----------|
| `double` | `float` | Builtin |
| `std::string` | `str` | Builtin |
| `std::vector<double>` | `list[float]` | `<pybind11/stl.h>` |
| `std::invalid_argument` | `ValueError` | Automatic exception translation |
| C++ class | Python class | `py::class_<>` |

### 3.3 The Import Chain

```python
from mylib import Calculator, power
```

Resolution path:
1. `mylib.__init__.py` executes `from mylib._core import Calculator, power`
2. Python searches for `_core.cpython-312-*.so` in the `mylib/` package directory
3. The shared library is `dlopen()`'d, which triggers `PYBIND11_MODULE` init
4. `Calculator` and `power` become available as Python objects

---

## 4. Prerequisites

Before building, ensure the following are installed:

| Requirement | Purpose | Install (Ubuntu/Debian) |
|-------------|---------|------------------------|
| Python 3.10+ | Runtime | `apt install python3` |
| python3-dev | Python C headers | `apt install python3-dev` |
| clang (or gcc) | C++ compiler | `apt install clang` |
| ninja-build (optional) | Faster parallel builds | `apt install ninja-build` |

> **Note:** `cmake` and `pybind11` are automatically installed during build isolation. Users do **not** need to pre-install them.

---

## 5. How the Build Works (The Invisible Hand)

This is the most important part: **the user never runs `cmake` or `make`**. One `pip install` does everything.

### 5.1 Build Pipeline

```
uv pip install -e "."
         │
         ▼
  pyproject.toml [build-system]
  requires = [setuptools, wheel, cmake, pybind11]
         │
         ▼
  Build isolation: uv creates a temporary venv
  with exactly the declared build dependencies
         │
         ▼
  setuptools reads pyproject.toml → executes setup.py
         │
         ▼
  setup.py: CMakeBuild.build_extension()
    ├── Detect compiler (CC/CXX env vars, default: clang)
    ├── Detect Python3 include dir (system, not isolated)
    ├── Locate pybind11 CMake config
    ├── cmake -S . -B build_temp/ [configure]
    └── cmake --build build_temp/      [compile]
         │
         ▼
  CMake builds two targets:
    1. core_lib     → static library (calculator.cpp.o)
    2. _core        → shared module (main.cpp.o + core_lib)
         │
         ▼
  _core.cpython-312-*.so → placed in mylib/
  mylib/__init__.py      → re-exports from _core
         │
         ▼
  Package installed ✓
```

### 5.2 Why `setup.py` is Needed

With the `setuptools.build_meta` backend, `pyproject.toml` alone can't invoke CMake. The `setup.py` acts as a bridge:

- **`CMakeExtension`**: tells setuptools "this isn't pure Python, delegate to CMake"
- **`CMakeBuild`**: overrides `build_ext` to run CMake instead of the default compiler
- **Python include dir resolution**: build isolation means `sys.prefix` points to a temp venv (which lacks Python headers). We explicitly query `/usr/bin/python3` to get the system include path.
- **pybind11 location**: `pybind11.get_cmake_dir()` locates the CMake config in the build-isolated venv.

> If using `scikit-build-core` or `meson-python` as the build backend, CMake invocation would be handled natively without a `setup.py`.

### 5.3 Build Isolation Explained

uv/setuptools creates a **temporary virtual environment** for the build step. This temp venv contains only the packages listed in `[build-system] requires`. It does **not** contain the user's installed packages.

This is why:
- `pybind11` must be in `build-system requires` (CMake needs its config)
- Python headers must be queried from the system Python (temp venv has no headers)
- `cmake` must be in `build-system requires` (build env needs the binary)

### 5.4 Output Location

CMake's `CMAKE_LIBRARY_OUTPUT_DIRECTORY` is set to the final install location:

```python
ext_path = Path(self.get_ext_fullpath(ext.name))  # .../mylib/_core.cpython-312-*.so
install_dir = ext_path.parent.resolve()            # .../mylib/
```

The `.so` file lands directly next to `__init__.py`, so Python's import system finds it immediately.

### 5.5 Debug Builds

By default, builds use `Release` mode. To build with debug symbols:

```bash
CMAKE_BUILD_TYPE=Debug uv pip install -e "."
```

---

## 6. C++ Compilation Details

### 6.1 CMake Target Hierarchy

```
Top-level CMakeLists.txt
├── add_subdirectory(src/cpp/core)
│   └── core_lib (STATIC library)
│       └── calculator.cpp
│
└── add_subdirectory(src/cpp/bindings)
    └── _core (SHARED MODULE)
        ├── main.cpp
        └── links against → core_lib
```

**Why two targets?** `core_lib` is a static library. The `_core` module links against it. This means:
- The core logic is compiled once
- Multiple binding modules could link to the same core (e.g., separate modules for different Python versions)

### 6.2 Compiler Configuration

| Setting | Value | Notes |
|---------|-------|-------|
| C++ Standard | C++17 | Modern features, widely available |
| Compiler | Defaults to clang, respects `CC`/`CXX` env vars | `CC=gcc CXX=g++` to use GCC |
| Flags (Clang only) | `-Wall -Wextra -Wpedantic` | Strict warnings, applied conditionally |
| Optimization (Clang only) | `-O3 -march=native` | Max performance for the host CPU |

> **Warning about `-march=native`:** This flag generates code optimized for the build machine's CPU. Binaries compiled with it **may crash on different CPUs** (especially older generations or different architectures). For distributable wheels, replace with a specific architecture target (e.g., `-march=x86-64`) or remove entirely.

### 6.3 Build Generator

The setup.py auto-detects **Ninja**. If available, it uses Ninja instead of Unix Makefiles for faster parallel builds.

### 6.4 C++17 Modern Attributes

The code uses `[[nodiscard]]` on `history()` and `summary()`:

```cpp
[[nodiscard]] std::vector<double> history() const;
[[nodiscard]] std::string summary() const;
```

This is a C++17 attribute that warns if the return value is ignored. Since these methods produce valuable data (operation history, state summary), ignoring their return is almost certainly a bug.

---

## 7. Python Package Structure

### 7.1 Entry Point

`src/python/mylib/__init__.py`:

```python
from mylib._core import Calculator, power

__all__ = ["Calculator", "power"]
__version__ = "0.1.0"
```

This is a **thin wrapper** — it re-exports everything from the C++ extension. The `__version__` is available at runtime:

```python
import mylib
print(mylib.__version__)  # "0.1.0"
```

### 7.2 Package Metadata

`pyproject.toml` declares:

- **Name**: `mylib`
- **Version**: `0.1.0`
- **Python**: `>=3.10`
- **Build backend**: `setuptools.build_meta`
- **Build dependencies**: setuptools, wheel, cmake, pybind11

---

## 8. Data Flow: From Python Call to C++ Execution

```
Python: calc = Calculator(10.0)
    │
    ▼
pybind11: py::init<double>()
    │
    ▼
C++:   new mylib::Calculator(10.0)
    │
    ▼
C++:   Calculator::Calculator(double initial_value) { current_ = initial_value; }
    │
    ▼
Returns a py::object wrapping the C++ instance back to Python


Python: result = calc.add(5.0)
    │
    ▼
pybind11: dispatches to Calculator::add(double)
    │
    ▼
C++:   current_ += 5.0; ops_.push_back(5.0); return current_;
    │
    ▼
pybind11: converts C++ double → Python float
    │
    ▼
Python: result = 15.0  ✓
```

### Exception Handling

C++ exceptions are automatically translated by pybind11:

```cpp
throw std::invalid_argument("division by zero");
```

↓ pybind11 automatic exception translation

```python
raise ValueError("division by zero")
```

---

## 9. Testing

The project uses **pytest** for testing (declared in `dev` dependencies):

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=mylib
```

Tests are located in `tests/test_calculator.py` and cover:
- Calculator initialization (default and custom values)
- All arithmetic operations (add, subtract, multiply, divide)
- Division by zero exception handling
- History tracking and accumulation
- Reset functionality
- `power()` function accuracy

---

## 10. Key Design Decisions

### 10.1 Why Not scikit-build?

scikit-build adds an abstraction layer between setuptools and CMake. For this project, a custom `setup.py` is:
- **Simpler to understand** — only ~70 lines of Python
- **Easier to debug** — full control over CMake arguments
- **More flexible** — can add custom logic (Ninja detection, system Python lookup)

Migrate to scikit-build-core only if CMake complexity grows (e.g., multi-platform wheels with `cibuildwheel`).

### 10.2 Why pybind11 Over Alternatives?

| Tool | Pros | Cons |
|------|------|------|
| **pybind11** | Mature, great docs, automatic type conversion | Slightly verbose for simple cases |
| nanobind | Faster compilation, smaller binaries | Newer, less ecosystem |
| Cython | Python-like syntax, fine-grained control | Different language, learning curve |
| ctypes | No compilation needed | Manual type mapping, slow |
| SWIG | Multi-language support | Generated code is hard to maintain |

### 10.3 Why Build Isolation?

Build isolation (enabled by default with modern setuptools) ensures:
- Reproducible builds regardless of user's installed packages
- No accidental dependency on non-declared packages
- Clean separation between build-time and run-time dependencies

The tradeoff: slightly slower first build (downloads cmake, pybind11 into temp venv).

---

## 11. Extending the Project

### 11.1 Adding a New C++ Module

1. Create `src/cpp/core/new_feature.hpp` and `new_feature.cpp`
2. Add sources to `src/cpp/core/CMakeLists.txt`
3. Add bindings in `src/cpp/bindings/main.cpp`
4. Re-run `uv pip install -e "."`

### 11.2 Adding a Pure-Python Module

Create `src/python/mylib/utils.py` — no C++ needed. Just import it:

```python
# src/python/mylib/__init__.py
from mylib._core import Calculator, power
from mylib.utils import helper_function
```

### 11.3 Multiple Extension Modules

To create a second extension module (e.g., `mylib._fast_math`):

1. Add new binding target in `src/cpp/bindings/`
2. Add another `CMakeExtension` in `setup.py`:

```python
setup(
    ext_modules=[
        CMakeExtension("mylib._core", sourcedir="."),
        CMakeExtension("mylib._fast_math", sourcedir="."),
    ],
    ...
)
```

### 11.4 Cross-Platform Notes

| Platform | Extension Suffix | Notes |
|----------|-----------------|-------|
| Linux | `.cpython-312-x86_64-linux-gnu.so` | ELF format |
| macOS | `.cpython-312-darwin.so` | Mach-O, may need `-undefined dynamic_lookup` |
| Windows | `.cp312-win_amd64.pyd` | PE format, requires MSVC or MinGW |

For multi-platform distribution, consider using **cibuildwheel** to automate building wheels for all targets.

---

## 12. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Could NOT find Python3` | Missing `python3-dev` | `apt install python3-dev` |
| `Could NOT find pybind11` | pybind11 not in build deps | Check `build-system requires` |
| `const correctness error` | Mutating methods marked `const` | Remove `const` from C++ signatures |
| Build succeeds but `import mylib` fails | `.so` in wrong location | Check `CMAKE_LIBRARY_OUTPUT_DIRECTORY` |
| Slow first build | Build isolation downloading deps | Expected; cached on subsequent builds |
| Binary crashes on another machine | `-march=native` CPU-specific code | Use generic arch flag for distribution |
