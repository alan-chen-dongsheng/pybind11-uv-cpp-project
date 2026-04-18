find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_core MODULE main.cpp)

target_link_libraries(_core PRIVATE core_lib)

target_include_directories(_core PRIVATE ${Python3_INCLUDE_DIRS})

set_target_properties(_core PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}"
)
