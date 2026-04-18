#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "calculator.hpp"

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "High-performance C++ calculator module";

    py::class_<mylib::Calculator>(m, "Calculator")
        .def(py::init<>(),
             "Create a Calculator initialized at 0.0")
        .def(py::init<double>(),
             "Create a Calculator with an initial value",
             py::arg("initial_value"))
        .def("add", &mylib::Calculator::add,
             "Add a value", py::arg("value"))
        .def("subtract", &mylib::Calculator::subtract,
             "Subtract a value", py::arg("value"))
        .def("multiply", &mylib::Calculator::multiply,
             "Multiply by a value", py::arg("value"))
        .def("divide", &mylib::Calculator::divide,
             "Divide by a value", py::arg("value"))
        .def("accumulate", &mylib::Calculator::accumulate,
             "Return the sum of all operations")
        .def("reset", &mylib::Calculator::reset,
             "Reset the calculator")
        .def("history", &mylib::Calculator::history,
             "Return operation history as a list")
        .def("summary", &mylib::Calculator::summary,
             "Return a summary string");

    m.def("power", &mylib::power,
          "Compute base^exponent",
          py::arg("base"), py::arg("exponent"));
}
