#!/usr/bin/env python3
"""Basic usage demonstration of mylib."""

from mylib import Calculator, power

# ── Calculator API ──────────────────────────────────────────────
calc = Calculator(10.0)
print(f"Initial:  {calc.summary()}")

calc.add(5.0)
print(f"After +5: {calc.summary()}")

calc.multiply(2.0)
print(f"After ×2: {calc.summary()}")

print(f"History:  {calc.history()}")
print(f"Total ops: {calc.accumulate()}")

# ── Free function ───────────────────────────────────────────────
print(f"\n2^10 = {power(2.0, 10.0)}")
