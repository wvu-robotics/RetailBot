#include <controller_interface/controller_interface_base.hpp>
#include <memory>
#include <queue>
#include <string>
#include <utility>
#include <vector>

#include "rclcpp/logging.hpp"
#include "tf2/LinearMath/Quaternion.h"
#include "hardware_interface/types/hardware_interface_type_values.hpp"

#include "rb_indiv_controller/rb_indiv_controller.hpp"

namespace rb_indiv_controller
{
	using controller_interface::interface_configuration_type;
	using controller_interface::InterfaceConfiguration;
	using hardware_interface::HW_IF_POSITION;
	using hardware_interface::HW_IF_VELOCITY;


	RbIndivController::RbIndivController()
		: controller_interface::ControllerInterface()
	{
	}

	controller_interface::CallbackReturn RbIndivController::on_init()
	{
		return controller_interface::CallbackReturn::SUCCESS;
	}

	controller_interface::CallbackReturn RbIndivController::on_configure(
			const rclcpp_lifecycle::State & previous_state)
	{
		return controller_interface::CallbackReturn::SUCCESS;
	}

	controller_interface::CallbackReturn RbIndivController::on_activate(
			const rclcpp_lifecycle::State & previous_state)
	{
		return controller_interface::CallbackReturn::SUCCESS;
	}

	controller_interface::CallbackReturn RbIndivController::on_deactivate(
			const rclcpp_lifecycle::State & previous_state)
	{
		return controller_interface::CallbackReturn::SUCCESS;
	}

	controller_interface::CallbackReturn RbIndivController::on_cleanup(
			const rclcpp_lifecycle::State & previous_state)
	{
		return controller_interface::CallbackReturn::SUCCESS;
	}

	controller_interface::CallbackReturn RbIndivController::on_error(
			const rclcpp_lifecycle::State & previous_state)
	{
		return controller_interface::CallbackReturn::SUCCESS;
	}


	controller_interface::return_type RbIndivController::update(
			const rclcpp::Time & time, const rclcpp::Duration & period)
	{
		return controller_interface::return_type::OK;
	}

	/**
	 * This is called by the controller_manager node. The
	 * InterfaceConfiguration struct must match those advertised by the
	 * hardware component. In the ros2 demo controllers they use a parameter
	 * library to configure names and number of interfaces.
	 * https://github.com/PickNikRobotics/generate_parameter_library
	 * This let's use YAML files to configure C++ code like we would for python.
	 *
	 * See the diff_drive controller CMakeLists.txt for an example of how compile
	 * and link our code against the parameter library.
	 * https://github.com/ros-controls/ros2_controllers/blob/master/diff_drive_controller/CMakeLists.txt
	 *
	 * The benefit here is we can have multiple controllers compatible with
	 * different robots so long as the physical design is the same (or
	 * similar enough, e.g. skid steer with 2,4,6,... wheels).
	 */

	controller_interface::InterfaceConfiguration RbIndivController::command_interface_configuration() const
	{
		std::vector<std::string> conf_names;
    conf_names.push_back(std::string("fr_wheel_joint") + "/" + HW_IF_VELOCITY);
    conf_names.push_back(std::string("br_wheel_joint") + "/" + HW_IF_VELOCITY);
    conf_names.push_back(std::string("fl_wheel_joint") + "/" + HW_IF_VELOCITY);
    conf_names.push_back(std::string("fl_wheel_joint") + "/" + HW_IF_VELOCITY);

		return {interface_configuration_type::INDIVIDUAL, conf_names};
	}

	controller_interface::InterfaceConfiguration RbIndivController::state_interface_configuration() const
		/*InterfaceConfiguration state_interface_configuration()*/
	{
		std::vector<std::string> conf_names;
    conf_names.push_back(std::string("fr_wheel_joint") + "/" + HW_IF_POSITION);
    conf_names.push_back(std::string("br_wheel_joint") + "/" + HW_IF_POSITION);
    conf_names.push_back(std::string("fl_wheel_joint") + "/" + HW_IF_POSITION);
    conf_names.push_back(std::string("fl_wheel_joint") + "/" + HW_IF_POSITION);

		return {interface_configuration_type::INDIVIDUAL, conf_names};
	}


} // namespace rb_indiv_controller

#include "class_loader/register_macro.hpp"
CLASS_LOADER_REGISTER_CLASS(
		rb_indiv_controller::RbIndivController, controller_interface::ControllerInterface)

#include "pluginlib/class_list_macros.hpp"


	/*PLUGINLIB_EXPORT_CLASS(*/
	/*rb_indiv_controller::RbIndivController,*/
	/*  controller_interface::ControllerInterface)*/
