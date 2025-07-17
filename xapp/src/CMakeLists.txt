cmake_minimum_required(VERSION 3.5)
project(sample-xapp)

set(CMAKE_CXX_STANDARD 17)

find_package(PkgConfig REQUIRED)
pkg_check_modules(RMR REQUIRED rmr)

add_executable(sample-xapp main.cpp)
target_link_libraries(sample-xapp ${RMR_LIBRARIES})
target_include_directories(sample-xapp PRIVATE ${RMR_INCLUDE_DIRS})
