import pytest
from mylib import Calculator, power


class TestCalculator:
    def test_default_init(self):
        calc = Calculator()
        assert calc.summary() == "Calculator(current=0.0, operations=0)"

    def test_custom_init(self):
        calc = Calculator(10.0)
        assert calc.summary() == "Calculator(current=10.0, operations=0)"

    def test_add(self):
        calc = Calculator()
        assert calc.add(5.0) == 5.0
        assert calc.add(3.0) == 8.0

    def test_subtract(self):
        calc = Calculator(10.0)
        assert calc.subtract(3.0) == 7.0

    def test_multiply(self):
        calc = Calculator(5.0)
        assert calc.multiply(3.0) == 15.0

    def test_divide(self):
        calc = Calculator(10.0)
        assert calc.divide(2.0) == 5.0

    def test_divide_by_zero(self):
        calc = Calculator(10.0)
        with pytest.raises(ValueError, match="division by zero"):
            calc.divide(0.0)

    def test_history(self):
        calc = Calculator()
        calc.add(1.0)
        calc.add(2.0)
        calc.subtract(1.0)
        assert calc.history() == [1.0, 2.0, -1.0]

    def test_accumulate(self):
        calc = Calculator()
        calc.add(10.0)
        calc.subtract(3.0)
        assert calc.accumulate() == 7.0

    def test_reset(self):
        calc = Calculator(5.0)
        calc.add(3.0)
        calc.reset()
        assert calc.summary() == "Calculator(current=0.0, operations=0)"


def test_power():
    assert power(2.0, 3.0) == 8.0
    assert power(5.0, 0.5) == pytest.approx(2.2360679775, rel=1e-6)
