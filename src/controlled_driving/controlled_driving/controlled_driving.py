import rclpy
from rclpy.node import Node
from rclpy.duration import Duration

#from twist_slip_msg.msg import TwistSlipStamped
from std_msgs.msg import Header
from geometry_msgs.msg import Twist, Vector3
import numpy as np

class WheelDrive(Node):
    def __init__(self):
        super().__init__("wheel_drive")
        #self.publisher = self.create_publisher(Twist, "/rb_base_controller/cmd_vel", 10)
        self.publisher = self.create_publisher(Twist, "/diff_drive_base_controller/cmd_vel_unstamped", 10)
        timer = self.create_timer(0.1, self.send_move)
        self.declare_parameter('max_speed', 0.3)
        self.declare_parameter('accel', 1.0)
        self.declare_parameter('duration', 10.0)

        self.max_speed = self.get_parameter('max_speed').get_parameter_value().double_value
        self.max_accel = self.get_parameter('accel').get_parameter_value().double_value
        self.duration = self.get_parameter('duration').get_parameter_value().double_value

        self.start_time = self.get_clock().now()
        self.current_time = None
        self.elapsed_time = 0.0

    def send_move(self):
        """
        Check if the elapse time is greater than 5. If it is then reset the
        start time. This should repeatedly call make_vals() with a value for t.
        """
        # Check if elapsed_time > 5
        if self.elapsed_time > self.duration:
            self.start_time = self.get_clock().now()
            msg = self.stop_vals()
            self.publisher.publish(msg)
            return

        self.current_time = self.get_clock().now()
        self.elapsed_time = (self.current_time - self.start_time).nanoseconds /1e9 
        print(f"Elaseped time: {self.elapsed_time}")


        msg = self.make_vals()

        self.publisher.publish(msg)
        self.get_logger().info('Published twist with slip values')

    def make_vals(self):
        """
        Return a Twist message object populated with values.
        """
        #a = 0.2 # Scale factor
        #b = 1  # Time scale factor

        a = self.max_speed
        b = self.max_accel

        t = self.elapsed_time
        half_duration = self.duration / 2

        if t <= half_duration:
            linear_velocity = self.max_speed * np.tanh(self.max_accel * t)
        # Deceleration phase
        else:
            time_in_deceleration = t - half_duration
            remaining_time = half_duration - time_in_deceleration  # Inverse time for deceleration
            linear_velocity = self.max_speed * np.tanh(self.max_accel * remaining_time)

        msg = Twist()
        msg.linear = Vector3()
        msg.linear.x = 1*linear_velocity # Forward speed m/s
        #msg.linear.x = 0.0 # Forward speed m/s
        msg.linear.y = 0.0  # Sideways speed m/s
        msg.linear.z = 0.0  # Vertical speed m/s
        msg.angular = Vector3()
        msg.angular.x = 0.0  # Roll rate
        msg.angular.y = 0.0  # Pitch rate
        #msg.angular.z = linear_velocity   # Yaw rate rad/s
        msg.angular.z = 0.0    # Yaw rate rad/s

        return msg

    def stop_vals(self):
        msg = Twist()
        #msg.header = Header()
        #msg.header.stamp = self.get_clock().now().to_msg()
        #msg.header.frame_id = "base_link"

        #msg.twist = Twist()
        msg.linear = Vector3()
        msg.linear.x = 0.0  # Forward speed m/s
        msg.linear.y = 0.0  # Sideways speed m/s
        msg.linear.z = 0.0  # Vertical speed m/s
        msg.angular = Vector3()
        msg.angular.x = 0.0  # Roll rate
        msg.angular.y = 0.0  # Pitch rate
        msg.angular.z = 0.0  # Yaw rate rad/s

        # Set the individual wheel slip values
        #msg.fl_wheel = 0.0  # Slip ratio for front left wheel. Actually the BR
        #msg.fr_wheel = 0.0  # Slip ratio for front right wheel. Actually FL
        #msg.br_wheel = 0.0  # Slip ratio for back right wheel. Actually FR
        #msg.bl_wheel = 0.0  # Slip ratio for back left wheel. Actually BL
        return msg

def main():
    rclpy.init()
    node = WheelDrive()
    rclpy.spin(node)

    pass

if __name__ == "__main__":
    main()
