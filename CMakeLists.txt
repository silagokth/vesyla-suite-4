cmake_minimum_required(VERSION 3.5)

project(vesyla)

# Find includes in corresponding build directories
set(CMAKE_INCLUDE_CURRENT_DIR ON)

# Instruct CMake to run moc automatically when needed.
set(CMAKE_AUTOMOC OFF)

# The project version number.
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/CHANGELOG.md" CHANGELOG_CONTENT)
string(REGEX MATCH "## \\[([0-9]+)\\.([0-9]+)\\.([0-9]+)\\]" _ ${CHANGELOG_CONTENT})
set(VERSION_MAJOR ${CMAKE_MATCH_1} CACHE STRING "Project major version number.")
set(VERSION_MINOR ${CMAKE_MATCH_2} CACHE STRING "Project minor version number.")
set(VERSION_PATCH ${CMAKE_MATCH_3} CACHE STRING "Project patch version number.")
mark_as_advanced(VERSION_MAJOR VERSION_MINOR VERSION_PATCH)

message(STATUS "Detected version ${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH} from CHANGELOG.md")

# set(VERSION_MAJOR 4 CACHE STRING "Project major version number.")
# set(VERSION_MINOR 0 CACHE STRING "Project minor version number.")
# set(VERSION_PATCH 3 CACHE STRING "Project patch version number.")
# mark_as_advanced(VERSION_MAJOR VERSION_MINOR VERSION_PATCH)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_SHARED_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/share/${PROJECT_NAME})
set(INSTALL_ARCHIVE_OUTPUT_DIRECTORY lib)
set(INSTALL_LIBRARY_OUTPUT_DIRECTORY lib)
set(INSTALL_RUNTIME_OUTPUT_DIRECTORY bin)
set(INSTALL_SHARED_OUTPUT_DIRECTORY share/${PROJECT_NAME})

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/modules/")

add_subdirectory("module/vs-manas")
add_subdirectory("module/vs-component")
add_subdirectory("module/vs-testcase")
add_subdirectory("module/vs-schedule")
add_subdirectory("module/vs-entry")
