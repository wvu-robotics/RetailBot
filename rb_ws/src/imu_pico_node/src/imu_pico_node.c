#include <stdio.h>

#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <stdlib.h>
#include <rclc/executor.h>
#include <std_msgs/msg/int32.h>
#include <sensor_msgs/msg/imu.h>
#include <geometry_msgs/msg/vector3.h>
#include <std_msgs/msg/header.h>
#include "rosidl_runtime_c/string_functions.h"
#include <rmw_microros/rmw_microros.h>

#include "pico/stdlib.h"
#include "pico_uart_transports.h"

#include "pico/binary_info.h"
#include "hardware/spi.h"



typedef struct {
	rcl_allocator_t allocator;
	rclc_support_t support;
	rcl_init_options_t init_options;
	rcl_node_t node;
	rcl_publisher_t publisher;
	rcl_timer_t timer;
	rclc_executor_t executor;
	sensor_msgs__msg__Imu msg;
} ros_state_t;

typedef struct {
	spi_inst_t *spi;
	uint8_t cs_pin;
} spi_state_t;

typedef struct{
	// Linear acceleraton.
	float x_lin_accel; // m/s^2
	float y_lin_accel;
	float z_lin_accel;

	// Angular velocity.
	float x_ang_vel; // rad/s
	float y_ang_vel;
	float z_ang_vel;
} spi_read_t;

// Globals.
ros_state_t ros_state;
const uint LED_PIN = 25;
spi_read_t spi_data;

// SPI globals.
#define BUF_LEN 14
// Add extra ttwo bytes to read PROD_ID so we can get last byte of actual
// request.
uint8_t out_buf[BUF_LEN] = {0x1E, 0x00, 0x22, 0x00, 0x026, 0x00, 
	0x12, 0x00,	0x16, 0x0, 0x1A, 0x00,
	0x70, 0x00};
uint8_t in_buf[BUF_LEN];                                      
uint8_t tail_byte;                                      
uint8_t zero_byte = 0x00;



void timer_callback(rcl_timer_t *timer, int64_t last_call_time)
{
	geometry_msgs__msg__Vector3 lin_vel;
	lin_vel.x = spi_data.x_lin_accel;
	lin_vel.y = spi_data.y_lin_accel;
	lin_vel.z = spi_data.z_lin_accel;

	geometry_msgs__msg__Vector3 ang_vel;
	ang_vel.x = spi_data.x_ang_vel;
	ang_vel.y = spi_data.y_ang_vel;
	ang_vel.z = spi_data.z_ang_vel;

	double lin_cov[9] = {
		0.002792528, 0, 0,
		0, 0.002792528, 0,
		0, 0, 0.002792528
	};

	double ang_cov[9] = 
		{
			0.00245, 0, 0,
			0, 0.00245, 0,
			0, 0 ,0.00245

		};

	//std_msgs__msg__Header__init(&ros_state.msg.header);

	// Assign the string "imu_link" to header.frame_id
	// Memory leak?
	/*rosidl_runtime_c__String__assign(&ros_state.msg.header.frame_id, "imu_link");*/

	// Sync time with the agent
	const int timeout_ms = 5000;
	rmw_uros_sync_session(timeout_ms);
	if (rmw_uros_epoch_synchronized())
	{
		int64_t time_ns = rmw_uros_epoch_nanos();
		ros_state.msg.header.stamp.sec = time_ns / 1000000000LL;
		ros_state.msg.header.stamp.nanosec = time_ns % 1000000000LL;
	}

	ros_state.msg.angular_velocity = ang_vel;
	ros_state.msg.linear_acceleration = lin_vel;
	//ros_state.msg.header = header;
	memcpy(ros_state.msg.linear_acceleration_covariance, lin_cov, sizeof(lin_cov));
	memcpy(ros_state.msg.angular_velocity_covariance, ang_cov, sizeof(ang_cov));

	//ros_state.msg.linear_acceleration_covariance = lin_cov;
	//ros_state.msg.angular_velocity_covariance = ang_cov;

	rcl_ret_t ret = rcl_publish(&ros_state.publisher, &ros_state.msg, NULL);
}

// SPI functions 
static inline void cs_select(){
	asm volatile("nop \n nop \n nop");
	gpio_put(PICO_DEFAULT_SPI_CSN_PIN, 0); //Active low.
	asm volatile("nop \n nop \n nop");
}

static inline void cs_deselect(){
	asm volatile("nop \n nop \n nop");
	gpio_put(PICO_DEFAULT_SPI_CSN_PIN, 1); //Active low.
	asm volatile("nop \n nop \n nop");
}

spi_state_t init_spi(spi_inst_t *spi, uint8_t cs_pin){
	spi_state_t spi_state;
	spi_state.spi = spi;
	spi_state.cs_pin = cs_pin;

	gpio_set_function(cs_pin, GPIO_FUNC_SPI);
	spi_init(spi, 500 * 1000);
	gpio_set_function(PICO_DEFAULT_SPI_RX_PIN, GPIO_FUNC_SPI);                      
	gpio_set_function(PICO_DEFAULT_SPI_SCK_PIN, GPIO_FUNC_SPI);                     
	gpio_set_function(PICO_DEFAULT_SPI_TX_PIN, GPIO_FUNC_SPI);                      
	gpio_init(PICO_DEFAULT_SPI_CSN_PIN);
	gpio_set_dir(PICO_DEFAULT_SPI_CSN_PIN, GPIO_OUT);

	return spi_state;
}

/*int init_ros(){*/
/*	//ros_state.allocator = rcl_get_default_allocator();*/
/**/
/*	//rclc_support_init(&ros_state.support, 0, NULL, &ros_state.allocator);*/
/**/
/*	rcl_ret_t ret = rclc_support_init(&ros_state.support, 0, NULL, &ros_state.allocator);*/
/*	if (ret != RCL_RET_OK) {*/
/*		//printf("Error initializing support: %s\n", rcl_get_error_string().str);*/
/*		return -1;*/
/*	}*/
/**/
/*	ros_state.node = rcl_get_zero_initialized_node();*/
/*	rclc_node_init_default(&ros_state.node, "pico_node_1", "", &ros_state.support);*/
/**/
/*	rclc_publisher_init_default(*/
/*			&ros_state.publisher,*/
/*			&ros_state.node,*/
/*			ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, Imu),*/
/*			"pico_publisher");*/
/**/
/*	rclc_timer_init_default(*/
/*			&ros_state.timer,*/
/*			&ros_state.support,*/
/*			RCL_MS_TO_NS(200), // Increase to 50?*/
/*			timer_callback);*/
/**/
/*	ros_state.executor = rclc_executor_get_zero_initialized_executor();*/
/*	rclc_executor_init(&ros_state.executor, &ros_state.support.context, 1, &ros_state.allocator);*/
/*	rclc_executor_add_timer(&ros_state.executor, &ros_state.timer);*/
/**/
/*	return 0;*/
/*}*/

int contact_agent()
{
	// Wait for agent successful ping for 2 minutes.
	const int timeout_ms = 1000; 
	const uint8_t attempts = 120;

	rcl_ret_t ret = rmw_uros_ping_agent(timeout_ms, attempts);

	if (ret != RCL_RET_OK)
	{
		// Unreachable agent, exiting program.
		printf("failed!\n");
		return ret;
	}
	return 0;
}

void spi_read()
{
	cs_select();
	// First response byte is garbage.
	spi_write_read_blocking(spi0, out_buf, in_buf, BUF_LEN); 
	cs_deselect();

	int16_t lin_x_g = (in_buf[2] << 8) | in_buf[3];
	int16_t lin_y_g = (in_buf[4] << 8) | in_buf[5];
	int16_t lin_z_g = (in_buf[6] << 8) | in_buf[7];

	int16_t ang_x_deg = (in_buf[8] << 8) | in_buf[9];
	int16_t ang_y_deg = (in_buf[10] << 8) | in_buf[11];
	int16_t ang_z_deg = (in_buf[12] << 8) | in_buf[13];

	// Convert from gees to m/s^2. LSB = 0.00025gees/LSB.
	spi_data.x_lin_accel = lin_x_g * 0.00025 * 9.80665;
	spi_data.y_lin_accel = lin_y_g * 0.00025 * 9.80665;
	spi_data.z_lin_accel = lin_z_g * 0.00025 * 9.80665;

	// Convert from deg/s to rad/s. LSB=0.02deg.
	spi_data.x_ang_vel = ang_x_deg * 0.02 * 0.0174533;
	spi_data.y_ang_vel = ang_y_deg * 0.02 * 0.0174533;
	spi_data.z_ang_vel = ang_z_deg * 0.02 * 0.0174533;
}

int init_ros(){
	std_msgs__msg__Header__init(&ros_state.msg.header);

	rmw_uros_set_custom_transport(
		true,
		NULL,
		pico_serial_transport_open,
		pico_serial_transport_close,
		pico_serial_transport_write,
		pico_serial_transport_read
	);
	ros_state.allocator = rcl_get_default_allocator();
	//rclc_support_init(&ros_state.support, 0, NULL, &ros_state.allocator);

	// Initialize and modify options (Set DOMAIN ID to 10)
rcl_init_options_t init_options = rcl_get_zero_initialized_init_options();
rcl_init_options_init(&init_options, ros_state.allocator);
/*rcl_init_options_set_domain_id(&init_options, 69);*/

	rcl_ret_t ret = rclc_support_init_with_options(&ros_state.support, 0, NULL, &init_options, &ros_state.allocator);
	if (ret != RCL_RET_OK) {
		//printf("Error initializing support: %s\n", rcl_get_error_string().str);
		return -1;
	}

//	ros_state.node = rcl_get_zero_initialized_node();
	rclc_node_init_default(&ros_state.node, "pico_node_1", "", &ros_state.support);

	rclc_publisher_init_default(
		&ros_state.publisher,
		&ros_state.node,
		ROSIDL_GET_MSG_TYPE_SUPPORT(sensor_msgs, msg, Imu),
		"/rb/imu");

	rclc_timer_init_default(
		&ros_state.timer,
		&ros_state.support,
		RCL_MS_TO_NS(5),
		timer_callback);

	ros_state.executor = rclc_executor_get_zero_initialized_executor();
	rclc_executor_init(&ros_state.executor, &ros_state.support.context, 1, &ros_state.allocator);
	rclc_executor_add_timer(&ros_state.executor, &ros_state.timer);

	return 0;
}

int main()
{
	stdio_init_all();
	gpio_init(LED_PIN);
	gpio_set_dir(LED_PIN, GPIO_OUT);

	contact_agent(); // 2s timeout.

	init_ros(); // Populates global ros_state_t struct.
	gpio_put(LED_PIN, 1);

	// Move here?
	rosidl_runtime_c__String__assign(&ros_state.msg.header.frame_id, "imu_link");
	// Set up SPI
	spi_state_t spi_state = init_spi(spi0, 5);

	while(true)
	{
		spi_read(); // Do other stuff between ros spins.
		// Give ROS control for some time.
		rclc_executor_spin_some(&ros_state.executor, RCL_MS_TO_NS(2));
	}

	return 0;
}
