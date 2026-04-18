# mylib

A high-performance C++ library exposed to Python via pybind11.

## Quick Start

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/get/uv | sh

# Create virtual environment and install
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/ -v

# Run example
uv run python examples/basic_usage.py
```

## Build

```bash
uv pip install -e "."
```

This triggers CMake to compile the C++ code with clang and installs the resulting
shared library as a Python extension module.
