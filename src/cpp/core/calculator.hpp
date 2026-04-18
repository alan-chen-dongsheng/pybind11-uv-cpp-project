#pragma once

#include <string>
#include <vector>

namespace mylib {

class Calculator {
public:
    Calculator();
    explicit Calculator(double initial_value);

    double add(double value) const;
    double subtract(double value) const;
    double multiply(double value) const;
    double divide(double value) const;

    double accumulate() const;
    void reset();

    [[nodiscard]] std::vector<double> history() const;
    [[nodiscard]] std::string summary() const;

private:
    double current_;
    std::vector<double> ops_;
};

double power(double base, double exponent);

} // namespace mylib
