cmake_minimum_required(VERSION 3.15)
project(AudioPractice VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Options
option(BUILD_TESTS "Build unit tests" ON)
option(BUILD_BENCHMARKS "Build performance benchmarks" ON)
option(USE_SIMD "Enable SIMD optimizations" ON)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 REQUIRED)

# Platform-specific settings
if(MSVC)
    add_compile_options(/W4 /WX)
    if(USE_SIMD)
        add_compile_options(/arch:AVX2)
    endif()
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Werror)
    if(USE_SIMD)
        add_compile_options(-mavx2 -mfma)
    endif()
endif()

# Include directories
include_directories(src/cpp)

# Collect source files
file(GLOB_RECURSE CPP_SOURCES src/cpp/*.cpp)

file(GLOB_RECURSE CPP_HEADERS
    src/cpp/core/*.h
    src/cpp/dsp/*.h
    src/cpp/effects/*.h
)

# Create static library for C++ code
add_library(audio_practice_core STATIC ${CPP_SOURCES})
target_compile_features(audio_practice_core PUBLIC cxx_std_17)

# Create Python module
pybind11_add_module(audio_practice_native src/python/bindings.cpp)
target_link_libraries(audio_practice_native PRIVATE audio_practice_core)

# Set properties for Python module
set_target_properties(audio_practice_native PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/python
)

# Tests
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Benchmarks
if(BUILD_BENCHMARKS)
    add_subdirectory(benchmarks)
endif()

# Installation
install(TARGETS audio_practice_core
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(FILES ${CPP_HEADERS}
    DESTINATION include/audio_practice
) 