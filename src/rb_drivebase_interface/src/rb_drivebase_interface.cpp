// Copyright 2021 ros2_control Development Team
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
#define _USE_MATH_DEFINES

#include "rb_drivebase_interface/rb_drivebase_interface.hpp"

#include <chrono>
#include <cmath>
#include <cstddef>
#include <limits>
#include <memory>
#include <vector>

#include "hardware_interface/lexical_casts.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"

#include "rb_drivebase_interface/RoboteqDevice.h"                                                                                                                                                  
#include "rb_drivebase_interface/ErrorCodes.h"                                                                                                                                                     
#include "rb_drivebase_interface/Constants.h"


namespace rb_drivebase_interface
{
	hardware_interface::CallbackReturn RbSysHardware::on_init(
			const hardware_interface::HardwareInfo & info)
	{
		if (
				hardware_interface::SystemInterface::on_init(info) !=
				hardware_interface::CallbackReturn::SUCCESS)
		{
			return hardware_interface::CallbackReturn::ERROR;
		}

		// resize the vectors here to be the same as the number of joints.
		hw_positions_.resize(info_.joints.size(), std::numeric_limits<double>::quiet_NaN());
		hw_velocities_.resize(info_.joints.size(), std::numeric_limits<double>::quiet_NaN());
		hw_commands_.resize(info_.joints.size(), std::numeric_limits<double>::quiet_NaN());
		encoder_counts_.resize(info_.joints.size(), std::numeric_limits<double>::quiet_NaN());
		currents_.resize(info_.joints.size(), std::numeric_limits<double>::quiet_NaN());

		// Connect the two roboteqs.
		int l_roboteq_status =	l_roboteq.Connect("/dev/left_roboteq");
		int r_roboteq_status = r_roboteq.Connect("/dev/right_roboteq");

		if (l_roboteq_status != RQ_SUCCESS)
		{// Put ROS fatal error here.  std::vector<hardware_interface::CommandInterface> command_interfaces;
		}
		if (r_roboteq_status != RQ_SUCCESS)
		{
		}

		for (const hardware_interface::ComponentInfo & joint : info_.joints)
		{
			// DiffBotSystem has exactly two states and one command interface on each joint
			/*
				 if (joint.command_interfaces.size() != 1)
				 {
				 RCLCPP_FATAL(
				 rclcpp::get_logger("DiffBotSystemHardware"),
				 "Joint '%s' has %zu command interfaces found. 1 expected.", joint.name.c_str(),
				 joint.command_interfaces.size());
				 return hardware_interface::CallbackReturn::ERROR;
				 }
				 */

			if (joint.command_interfaces[0].name != hardware_interface::HW_IF_VELOCITY)
			{
				RCLCPP_FATAL(
						rclcpp::get_logger("DiffBotSystemHardware"),
						"Joint '%s' have %s command interfaces found. '%s' expected.", joint.name.c_str(),
						joint.command_interfaces[0].name.c_str(), hardware_interface::HW_IF_VELOCITY);
				return hardware_interface::CallbackReturn::ERROR;
			}

			/*
				 if (joint.state_interfaces.size() != 2)
				 {
				 RCLCPP_FATAL(
				 rclcpp::get_logger("DiffBotSystemHardware"),
				 "Joint '%s' has %zu state interface. 2 expected.", joint.name.c_str(),
				 joint.state_interfaces.size());
				 return hardware_interface::CallbackReturn::ERROR;
				 }
				 */

			if (joint.state_interfaces[0].name != hardware_interface::HW_IF_POSITION)
			{
				RCLCPP_FATAL(
						rclcpp::get_logger("DiffBotSystemHardware"),
						"Joint '%s' have '%s' as first state interface. '%s' expected.", joint.name.c_str(),
						joint.state_interfaces[0].name.c_str(), hardware_interface::HW_IF_POSITION);
				return hardware_interface::CallbackReturn::ERROR;
			}

			if (joint.state_interfaces[1].name != hardware_interface::HW_IF_VELOCITY)
			{
				RCLCPP_FATAL(
						rclcpp::get_logger("DiffBotSystemHardware"),
						"Joint '%s' have '%s' as second state interface. '%s' expected.", joint.name.c_str(),
						joint.state_interfaces[1].name.c_str(), hardware_interface::HW_IF_VELOCITY);
				return hardware_interface::CallbackReturn::ERROR;
			}
		}

		l_roboteq.SetCommand(_EX, 1);
		l_roboteq.SetCommand(_EX, 2);
		r_roboteq.SetCommand(_EX, 1);
		r_roboteq.SetCommand(_EX, 2);

		// reset encoder couunt
		l_roboteq.SetCommand(_SENCNTR,1,0); 
		l_roboteq.SetCommand(_SENCNTR,2,0); 
		r_roboteq.SetCommand(_SENCNTR,1,0); 
		r_roboteq.SetCommand(_SENCNTR,2,0); 

		l_roboteq.SetCommand(_MGO, 1);
		l_roboteq.SetCommand(_MGO, 2);
		r_roboteq.SetCommand(_MGO, 1);
		r_roboteq.SetCommand(_MGO, 2);

		return hardware_interface::CallbackReturn::SUCCESS;
	}

	/*
	 * This fella is how the controller gets access to the hardware. We pass out
	 * pointers to the state interfaces from this function. This is also how it
	 * finds the names of the joints since they are passed back in
	 * info_joints[i].name. Neat.
	 */
	std::vector<hardware_interface::StateInterface> RbSysHardware::export_state_interfaces()
	{
		std::vector<hardware_interface::StateInterface> state_interfaces;

		// Iterate for num of joints. Add a StateInterface objects for each joint.
		for (auto i = 0u; i < info_.joints.size(); i++)
		{
			state_interfaces.emplace_back(hardware_interface::StateInterface(
						info_.joints[i].name, hardware_interface::HW_IF_POSITION, &hw_positions_[i]));
			state_interfaces.emplace_back(hardware_interface::StateInterface(
						info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &hw_velocities_[i]));
			state_interfaces.emplace_back(hardware_interface::StateInterface(
						info_.joints[i].name, "encoder_count", &encoder_counts_[i]));
			state_interfaces.emplace_back(hardware_interface::StateInterface(
						info_.joints[i].name, "current", &currents_[i]));
		}

		return state_interfaces;
	}

	std::vector<hardware_interface::CommandInterface> RbSysHardware::export_command_interfaces()
	{
		std::vector<hardware_interface::CommandInterface> command_interfaces;
		// Iterate for each joint. Create a CommandInterface object for each and
		// return. This is how the resource manager blaabaaaaaaads 
		for (auto i = 0u; i < info_.joints.size(); i++)
		{
			command_interfaces.emplace_back(hardware_interface::CommandInterface(
						info_.joints[i].name, hardware_interface::HW_IF_VELOCITY, &hw_commands_[i]));
		}

		return command_interfaces;
	}

	hardware_interface::CallbackReturn RbSysHardware::on_activate(
			const rclcpp_lifecycle::State & /*previous_state*/)
	{
		// set some default values
		for (auto i = 0u; i < hw_positions_.size(); i++)
		{
			if (std::isnan(hw_positions_[i]))
			{
				hw_positions_[i] = 0;
				hw_velocities_[i] = 0;
				hw_commands_[i] = 0;
				encoder_counts_[i] = 5.0;
				currents_[i] = 0.0;
			}
		}
		RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Successfully activated!");

		return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::CallbackReturn RbSysHardware::on_deactivate(
			const rclcpp_lifecycle::State & /*previous_state*/)
	{
		l_roboteq.Disconnect();
		r_roboteq.Disconnect();

		RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Successfully deactivated!");

		return hardware_interface::CallbackReturn::SUCCESS;
	}

	hardware_interface::return_type RbSysHardware::read(
			const rclcpp::Time & /*time*/, const rclcpp::Duration & period)
	{

		int l_back_int;
		int l_front_int;
		int r_back_int; 
		int r_front_int;

		// Left channel MOT1 is front, MOT2 is back.
		// Right channel MOT1 is back mot2 is front.
		l_roboteq.GetValue(_ABSPEED,2, l_back_int);
		l_roboteq.GetValue(_ABSPEED,1, l_front_int);
		r_roboteq.GetValue(_ABSPEED,2, r_back_int);
		r_roboteq.GetValue(_ABSPEED,1, r_front_int);

		double l_back = l_back_int;
		double l_front = l_front_int;
		double r_back = r_back_int; 
		double r_front = r_front_int;

		//RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "l_back=%f",l_back);
		// Gett command from 
		//int mult = 12 * (60 / (2*3.14159));
		// command = mult * vel
		// vel = read / mult
		//double mult = 12 * (60 / (2*3.14159));

		/*l_back = double(l_back) / mult;
			l_front=double(l_front) / mult;
			r_back=double(r_back) / mult;
			r_front=double(r_front) / mult;
			*/

		//RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Encoders: l_back=%d, l_front=%d, r_back=%d, r_front=%d", l_back, l_front, r_back, r_front);
		hw_velocities_[3] = double(l_back);
		hw_velocities_[2] = double(l_front);
		hw_velocities_[1] = double(r_back);
		hw_velocities_[0] = double(r_front);

		// get wheel positions.
		int pos_l_back_int;
		int pos_l_front_int;
		int pos_r_back_int;
		int pos_r_front_int;

		// Left channel MOT1 is front, MOT2 is back.
		// Right channel MOT1 is back mot2 is front.
		l_roboteq.GetValue(_ABCNTR,2, pos_l_back_int);
		l_roboteq.GetValue(_ABCNTR,1, pos_l_front_int);
		r_roboteq.GetValue(_ABCNTR,2, pos_r_back_int);
		r_roboteq.GetValue(_ABCNTR,1, pos_r_front_int);


		double ppr = 6480.0;
		//double ppr = 61819.0;
		double pi = 3.14159;

		// Num of revolutions in rads
		double pos_l_back = (pos_l_back_int / ppr) * 2*pi;
		double pos_r_back = (pos_r_back_int / ppr) * 2*pi;
		double pos_l_front= (pos_l_front_int / ppr) * 2*pi;
		double pos_r_front = (pos_r_front_int / ppr) * 2*pi;

		hw_positions_[3] = pos_l_back;
		hw_positions_[2] = pos_l_front;
		hw_positions_[1] = pos_r_back;
		hw_positions_[0] = pos_r_front;

		//	RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "pos_l_back=%f",pos_l_back);
		//	RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "Encoders: pos_l_back=%f, pos_l_front=%f, pos_r_back=%f, pos_r_front=%f", pos_l_back, pos_l_front, pos_r_back, pos_r_front);

		// Get encoder counts.
		/*int encoder_l_back_int = 0;*/
		/*int encoder_l_front_int = 0;*/
		/*int encoder_r_back_int = 0;*/
		/*int encoder_r_front_int = 0;*/

		/*l_roboteq.GetValue(_MOTAMPS, 2, encoder_l_back_int); */
		/*l_roboteq.GetValue(_MOTAMPS, 1, amp_l_front_int);*/
		/*r_roboteq.GetValue(_MOTAMPS, 1, amp_r_back_int);*/
		/*r_roboteq.GetValue(_MOTAMPS, 2, amp_r_front_int);*/

		encoder_counts_[3] = double(pos_l_back_int);
		encoder_counts_[2] = double(pos_l_front_int);
		encoder_counts_[1] = double(pos_r_back_int);
		encoder_counts_[0] = double(pos_r_front_int);


		// Read current values
		int amp_l_back_int = 0;
		int amp_l_front_int = 0;
		int amp_r_back_int = 0;
		int amp_r_front_int = 0;

		l_roboteq.GetValue(_MOTAMPS, 2, amp_l_back_int); 
		l_roboteq.GetValue(_MOTAMPS, 1, amp_l_front_int);
		r_roboteq.GetValue(_MOTAMPS, 2, amp_r_back_int);
		r_roboteq.GetValue(_MOTAMPS, 1, amp_r_front_int);

		//RCLCPP_INFO(rclcpp::get_logger("DiffBotSystemHardware"), "amp_l_back=%f",amp_l_back_int);

		currents_[3] = double(amp_l_back_int);
		currents_[2] = double(amp_l_front_int);
		currents_[1] = double(amp_r_back_int);
		currents_[0] = double(amp_r_front_int);

		return hardware_interface::return_type::OK;
	}

	hardware_interface::return_type rb_drivebase_interface::RbSysHardware::write(
			const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
	{
		//	RCLCPP_INFO(
		//rclcpp::get_logger("DiffBotSystemHardware"), "Got command %.5f for '%s'!", hw_commands_[1],
		//		info_.joints[1].name.c_str());

		int mult = 12 * (60 / (2*3.14159));

		// Left channel MOT1 is front, MOT2 is back.
		// Right channel MOT1 is back mot2 is front.
		l_roboteq.SetCommand(_GO,2, mult * hw_commands_[3]); // Move back left.
		l_roboteq.SetCommand(_GO,1, mult * hw_commands_[2]);
		r_roboteq.SetCommand(_GO,2, mult * hw_commands_[1]); // Move back right
		r_roboteq.SetCommand(_GO,1, mult * hw_commands_[0]);

		return hardware_interface::return_type::OK;
	}

}  // namespace ros2_control_demo_example_2

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(
		rb_drivebase_interface::RbSysHardware, hardware_interface::SystemInterface)
