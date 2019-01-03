cmake_minimum_required(VERSION 2.8.12)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
project(baloo)

add_subdirectory(pybind11)

ENABLE_TESTING()

add_subdirectory(src/baloo)