cmake_minimum_required(VERSION 2.8.12)
project(baloo)

add_subdirectory(pybind11)

ENABLE_TESTING()

add_subdirectory(src/baloo)