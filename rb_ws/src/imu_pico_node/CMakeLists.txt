cmake_minimum_required(VERSION 3.13)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Check if the PICO_SDK_PATH has been set.
if(NOT DEFINED ENV{PICO_SDK_PATH})
  message(FATAL_ERROR "PICO_SDK_PATH environment variable is not defined")
endif()

#include(../deps/pico-sdk/pico_sdk_init.cmake)
include($ENV{PICO_SDK_PATH}/pico_sdk_init.cmake)

project(imu_pico_node)

pico_sdk_init()

link_directories(../micro_ros_raspberrypi_pico_sdk/libmicroros/)

add_executable(imu_pico
			${CMAKE_CURRENT_SOURCE_DIR}/src/pico_uart_transport.c
			${CMAKE_CURRENT_SOURCE_DIR}/src/imu_pico_node.c
		)
target_link_libraries(imu_pico
		pico_stdlib
		microros
		hardware_spi
		)

target_include_directories(imu_pico PUBLIC
		# How *should* I do this?
		#$ENV{PICO_SDK_PATH}/
		../micro_ros_raspberrypi_pico_sdk/libmicroros/include
		)


pico_enable_stdio_usb(imu_pico 1)
pico_enable_stdio_uart(imu_pico 0)
add_compile_definitions(PICO_UART_ENABLE_CRLF_SUPPORT=0)
add_compile_definitions(PICO_STDIO_ENABLE_CRLF_SUPPORT=0)
add_compile_definitions(PICO_STDIO_DEFAULT_CRLF=0)


pico_add_extra_outputs(imu_pico)
