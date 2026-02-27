cmake_minimum_required(VERSION 3.16)
project(event_processor VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Threads REQUIRED)
find_package(CURL REQUIRED)

include_directories(include)

add_library(processor_lib
    src/thread_pool.cpp
    src/event_queue.cpp
    src/event_processor.cpp
)

target_link_libraries(processor_lib PRIVATE Threads::Threads CURL::libcurl)

add_executable(event_processor src/main.cpp)
target_link_libraries(event_processor PRIVATE processor_lib Threads::Threads CURL::libcurl)

enable_testing()
add_executable(test_processor tests/test_processor.cpp)
target_link_libraries(test_processor PRIVATE processor_lib Threads::Threads CURL::libcurl)
add_test(NAME test_processor COMMAND test_processor)
