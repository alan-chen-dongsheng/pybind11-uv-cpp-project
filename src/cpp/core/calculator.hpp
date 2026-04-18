#pragma once

#include <string>
#include <vector>

namespace mylib {

class Calculator {
public:
    Calculator();
    explicit Calculator(double initial_value);

    double add(double value);
    double subtract(double value);
    double multiply(double value);
    double divide(double value);

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
