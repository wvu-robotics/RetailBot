def zero_twist(msg):
    msg.fl_wheel = 0.0
    msg.bl_wheel = 0.0
    msg.br_wheel = 0.0
    msg.fr_wheel = 0.0
    msg.twist.linear.x = 0.0
    msg.twist.linear.y = 0.0
    msg.twist.linear.z = 0.0
    msg.twist.angular.x = 0.0
    msg.twist.angular.y = 0.0
    msg.twist.angular.z = 0.0
    msg.header.stamp.sec = 0
    msg.header.stamp.nanosec = 0
    msg.header.frame_id = ''
    # msg.twist.linear.x = 0.0
    # msg.twist.linear.y = 0.0
    # msg.twist.linear.z = 0.0
    # msg.twist.angular.x = 0.0
    # msg.twist.angular.y = 0.0
    # msg.twist.angular.z = 0.0
    # msg.header.stamp.sec = 0
    # msg.header.stamp.nanosec = 0
    # msg.header.frame_id = ''
    return msg
