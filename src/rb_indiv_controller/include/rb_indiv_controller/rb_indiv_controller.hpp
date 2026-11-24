#ifndef DIFF_DRIVE_CONTROLLER__DIFF_DRIVE_CONTROLLER_HPP_
#define DIFF_DRIVE_CONTROLLER__DIFF_DRIVE_CONTROLLER_HPP_

#include <chrono>
#include <memory>
#include <queue>
#include <string>
#include <vector>

#include "geometry_msgs/msg/twist_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2_msgs/msg/tf_message.hpp"

#include "controller_interface/controller_interface.hpp"

namespace rb_indiv_controller
{


	class RbIndivController : public controller_interface::ControllerInterface
	{
		using TwistStamped = geometry_msgs::msg::TwistStamped;
		public:
			RbIndivController();

			controller_interface::InterfaceConfiguration command_interface_configuration() const override;

			controller_interface::InterfaceConfiguration state_interface_configuration() const override;

			controller_interface::return_type update(
					const rclcpp::Time & time, const rclcpp::Duration & period) override;

			controller_interface::CallbackReturn on_init() override;

			controller_interface::CallbackReturn on_configure(
					const rclcpp_lifecycle::State & previous_state) override;

			controller_interface::CallbackReturn on_activate(
					const rclcpp_lifecycle::State & previous_state) override;

			controller_interface::CallbackReturn on_deactivate(
					const rclcpp_lifecycle::State & previous_state) override;

			controller_interface::CallbackReturn on_cleanup(
					const rclcpp_lifecycle::State & previous_state) override;

			controller_interface::CallbackReturn on_error(
					const rclcpp_lifecycle::State & previous_state) override;

		private:
	};

}



#endif  // DIFF_DRIVE_CONTROLLER__DIFF_DRIVE_CONTROLLER_HPP_

