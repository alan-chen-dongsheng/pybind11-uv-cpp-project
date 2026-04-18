cmake_minimum_required(VERSION 3.26)
project(mylib LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    add_compile_options(-Wall -Wextra -Wpedantic -O3 -march=native)
endif()

add_subdirectory(src/cpp/core)
add_subdirectory(src/cpp/bindings)
