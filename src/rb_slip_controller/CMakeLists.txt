cmake_minimum_required(VERSION 3.16)
project(rb_slip_controller)

if(CMAKE_CXX_COMPILER_ID MATCHES "(GNU|Clang)")
  add_compile_options(-Wall -Wextra -Werror=conversion -Werror=unused-but-set-variable
                      -Werror=return-type -Werror=shadow -Werror=format -Werror=range-loop-construct
                      -Werror=missing-braces)
endif()

# using this instead of visibility macros
# S1 from https://github.com/ros-controls/ros2_controllers/issues/1053
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

set(THIS_PACKAGE_INCLUDE_DEPENDS
  control_toolbox
  controller_interface
  generate_parameter_library
  geometry_msgs
  hardware_interface
  nav_msgs
  pluginlib
  rclcpp
  rclcpp_lifecycle
  rcpputils
  realtime_tools
  tf2
  tf2_msgs
	twist_slip_msg
)

find_package(ament_cmake REQUIRED)
find_package(backward_ros REQUIRED)
foreach(Dependency IN ITEMS ${THIS_PACKAGE_INCLUDE_DEPENDS})
  find_package(${Dependency} REQUIRED)
endforeach()
add_compile_definitions(RCPPUTILS_VERSION_MAJOR=${rcpputils_VERSION_MAJOR})
add_compile_definitions(RCPPUTILS_VERSION_MINOR=${rcpputils_VERSION_MINOR})

generate_parameter_library(rb_slip_controller_parameters
  src/rb_slip_controller_parameter.yaml
  include/rb_slip_controller/custom_validators.hpp
)

add_library(rb_slip_controller SHARED
  src/rb_slip_controller.cpp
  src/odometry.cpp
)
target_compile_features(rb_slip_controller PUBLIC cxx_std_17)
target_include_directories(rb_slip_controller PUBLIC
  $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/rb_slip_controller>
)
target_link_libraries(rb_slip_controller
  PUBLIC
    rb_slip_controller_parameters)
ament_target_dependencies(rb_slip_controller PUBLIC ${THIS_PACKAGE_INCLUDE_DEPENDS})
pluginlib_export_plugin_description_file(controller_interface
	rb_slip_controller_plugin.xml)

# if(BUILD_TESTING)
#   find_package(ament_cmake_gmock REQUIRED)
#   find_package(controller_manager REQUIRED)
#   find_package(ros2_control_test_assets REQUIRED)
#
#   ament_add_gmock(test_rb_slip_controller
#     test/test_rb_slip_controller.cpp
#   )
#   target_link_libraries(test_rb_slip_controller
#     rb_slip_controller
#   )
#   ament_target_dependencies(test_rb_slip_controller
#     geometry_msgs
#     hardware_interface
#     nav_msgs
#     rclcpp
#     rclcpp_lifecycle
#     realtime_tools
#     tf2
#     tf2_msgs
#   )
#
#   add_definitions(-DTEST_FILES_DIRECTORY="${CMAKE_CURRENT_SOURCE_DIR}/test")
#   ament_add_gmock(test_load_rb_slip_controller test/test_load_rb_slip_controller.cpp)
#   ament_target_dependencies(test_load_rb_slip_controller
#     controller_manager
#     ros2_control_test_assets
#   )
# endif()

install(
  DIRECTORY include/
  DESTINATION include/rb_slip_controller
)
install(DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)
install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)
file(GLOB SCRIPT_FILES scripts/*.py)
install(PROGRAMS 
	${SCRIPT_FILES}
  DESTINATION lib/${PROJECT_NAME}
)
install(TARGETS rb_slip_controller rb_slip_controller_parameters
  EXPORT export_rb_slip_controller
  RUNTIME DESTINATION bin
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
)

ament_export_targets(export_rb_slip_controller HAS_LIBRARY_TARGET)
ament_export_dependencies(${THIS_PACKAGE_INCLUDE_DEPENDS})
ament_package()
