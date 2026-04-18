#include "calculator.hpp"
#include <numeric>
#include <cmath>
#include <sstream>
#include <iomanip>
#include <stdexcept>

namespace mylib {

Calculator::Calculator() : current_(0.0) {}

Calculator::Calculator(double initial_value) : current_(initial_value) {}

double Calculator::add(double value) {
    current_ += value;
    ops_.push_back(value);
    return current_;
}

double Calculator::subtract(double value) {
    current_ -= value;
    ops_.push_back(-value);
    return current_;
}

double Calculator::multiply(double value) {
    current_ *= value;
    ops_.push_back(value);
    return current_;
}

double Calculator::divide(double value) {
    if (value == 0.0) {
        throw std::invalid_argument("division by zero");
    }
    current_ /= value;
    ops_.push_back(value);
    return current_;
}

double Calculator::accumulate() const {
    return std::accumulate(ops_.begin(), ops_.end(), 0.0);
}

void Calculator::reset() {
    current_ = 0.0;
    ops_.clear();
}

std::vector<double> Calculator::history() const {
    return ops_;
}

std::string Calculator::summary() const {
    std::ostringstream oss;
    oss << std::fixed << std::setprecision(1);
    oss << "Calculator(current=" << current_
        << ", operations=" << ops_.size() << ")";
    return oss.str();
}

double power(double base, double exponent) {
    return std::pow(base, exponent);
}

} // namespace mylib
