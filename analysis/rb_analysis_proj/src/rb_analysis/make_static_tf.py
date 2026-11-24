from tf2_ros import TransformStamped
from tf2_msgs.msg import TFMessage


def make_static_tf() -> TFMessage:
    # Hack in static transforms for the robot.
    body_assembly_tf = TransformStamped()
    body_assembly_tf.header.frame_id = "base_link"
    body_assembly_tf.child_frame_id = "body_assembly"
    body_assembly_tf.transform.translation.x = 0.0
    body_assembly_tf.transform.translation.y = 0.0
    body_assembly_tf.transform.translation.z = 0.0
    body_assembly_tf.transform.rotation.x = 0.0
    body_assembly_tf.transform.rotation.y = 0.0
    body_assembly_tf.transform.rotation.z = 0.0
    body_assembly_tf.transform.rotation.w = 1.0

    bl_tire_tf = TransformStamped()
    bl_tire_tf.header.frame_id = "bl_wheel"
    bl_tire_tf.child_frame_id = "bl_patch"
    bl_tire_tf.transform.translation.x = 4.85722573273506e-17
    bl_tire_tf.transform.translation.y = 5.551115123125783e-17
    bl_tire_tf.transform.translation.z = -0.1337945000000001
    bl_tire_tf.transform.rotation.x = -7.216449660051615e-16
    bl_tire_tf.transform.rotation.y = 3.885780586188474e-16
    bl_tire_tf.transform.rotation.z = -2.775557561553138e-16
    bl_tire_tf.transform.rotation.w = 1.0

    br_tire_tf = TransformStamped()
    br_tire_tf.header.frame_id = "br_wheel"
    br_tire_tf.child_frame_id = "br_patch"
    br_tire_tf.transform.translation.x = 6.938893903907228e-18
    br_tire_tf.transform.translation.y = 0.0
    br_tire_tf.transform.translation.z = -0.1337945000000001
    br_tire_tf.transform.rotation.x = 7.215346115250174e-16
    br_tire_tf.transform.rotation.y = -1.5651472852649807e-16
    br_tire_tf.transform.rotation.z = -2.7929047963014134e-16
    br_tire_tf.transform.rotation.w = 1.0

    fl_tire_tf = TransformStamped()
    fl_tire_tf.header.frame_id = "fl_wheel"
    fl_tire_tf.child_frame_id = "fl_patch"
    fl_tire_tf.transform.translation.x = 0.0
    fl_tire_tf.transform.translation.y = 0.0
    fl_tire_tf.transform.translation.z = -0.1337945000000001
    fl_tire_tf.transform.rotation.x = 1.1102230246264002e-16
    fl_tire_tf.transform.rotation.y = -1.5593048718502875e-30
    fl_tire_tf.transform.rotation.z = 8.226802350443992e-29
    fl_tire_tf.transform.rotation.w = 1.0

    fr_tire_tf = TransformStamped()
    fr_tire_tf.header.frame_id = "fr_wheel"
    fr_tire_tf.child_frame_id = "fr_patch"
    fr_tire_tf.transform.translation.x = 6.938893903907228e-18
    fr_tire_tf.transform.translation.y = 0.0
    fr_tire_tf.transform.translation.z = -0.13379450000000004
    fr_tire_tf.transform.rotation.x = -7.831291700877619e-17
    fr_tire_tf.transform.rotation.y = 2.4865692621727728e-30
    fr_tire_tf.transform.rotation.z = -4.190823558985819e-31
    fr_tire_tf.transform.rotation.w = 1.0

    vicon_ball_tf = TransformStamped()
    vicon_ball_tf.header.frame_id = "base_link"
    vicon_ball_tf.child_frame_id = "vicon_ball"
    vicon_ball_tf.transform.translation.x = 0.006846331482470505
    vicon_ball_tf.transform.translation.y = 0.33905758449404216
    vicon_ball_tf.transform.translation.z = 0.032512000000000346
    vicon_ball_tf.transform.rotation.x = 4.279977145501479e-16
    vicon_ball_tf.transform.rotation.y = -5.427076622916737e-16
    vicon_ball_tf.transform.rotation.z = -3.901640706876909e-16
    vicon_ball_tf.transform.rotation.w = 1.0

    bl_wheel_tf = TransformStamped()
    bl_wheel_tf.header.frame_id = "base_link"
    bl_wheel_tf.child_frame_id = "bl_wheel"
    bl_wheel_tf.transform.translation.x = -0.3233536684657514
    bl_wheel_tf.transform.translation.y = 0.2571425844940418
    bl_wheel_tf.transform.translation.z = 0.032511999948221106
    # bl_wheel_tf.transform.rotation.x = 0.500000000000003
    # bl_wheel_tf.transform.rotation.y = 0.4999999999999971
    # bl_wheel_tf.transform.rotation.z = 0.4999999999999971
    # bl_wheel_tf.transform.rotation.w = -0.5000000000000032
    bl_wheel_tf.transform.rotation.x = 0.0
    bl_wheel_tf.transform.rotation.y = 0.0
    bl_wheel_tf.transform.rotation.z = 0.0
    bl_wheel_tf.transform.rotation.w = 1.0

    br_wheel_tf = TransformStamped()
    br_wheel_tf.header.frame_id = "base_link"
    br_wheel_tf.child_frame_id = "br_wheel"
    br_wheel_tf.transform.translation.x = -0.3233536685693126
    br_wheel_tf.transform.translation.y = -0.25720741550594695
    br_wheel_tf.transform.translation.z = 0.03251199994823433
    # br_wheel_tf.transform.rotation.x = 0.500000000000018
    # br_wheel_tf.transform.rotation.y = 0.4999999999999821
    # br_wheel_tf.transform.rotation.z = 0.5000000000000037
    # br_wheel_tf.transform.rotation.w = -0.49999999999999667
    br_wheel_tf.transform.rotation.x = 0.0
    br_wheel_tf.transform.rotation.y = 0.0
    br_wheel_tf.transform.rotation.z = 0.0
    br_wheel_tf.transform.rotation.w = 1.0

    fl_wheel_tf = TransformStamped()
    fl_wheel_tf.header.frame_id = "base_link"
    fl_wheel_tf.child_frame_id = "fl_wheel"
    fl_wheel_tf.transform.translation.x = 0.3370463315342484
    fl_wheel_tf.transform.translation.y = 0.2571425844940314
    fl_wheel_tf.transform.translation.z = 0.032511999948229245
    # fl_wheel_tf.transform.rotation.x = 0.5000000000000122
    # fl_wheel_tf.transform.rotation.y = 0.4999999999999878
    # fl_wheel_tf.transform.rotation.z = 0.5000000000000075
    # fl_wheel_tf.transform.rotation.w = -0.49999999999999245
    fl_wheel_tf.transform.rotation.x = 0.0
    fl_wheel_tf.transform.rotation.y = 0.0
    fl_wheel_tf.transform.rotation.z = 0.0
    fl_wheel_tf.transform.rotation.w = 1.0

    fr_wheel_tf = TransformStamped()
    fr_wheel_tf.header.frame_id = "base_link"
    fr_wheel_tf.child_frame_id = "fr_wheel"
    fr_wheel_tf.transform.translation.x = 0.33704633143069057
    fr_wheel_tf.transform.translation.y = -0.25720741550595705
    fr_wheel_tf.transform.translation.z = 0.032511999948221744
    # fr_wheel_tf.transform.rotation.x = 0.500000000000008
    # fr_wheel_tf.transform.rotation.y = 0.499999999999992
    # fr_wheel_tf.transform.rotation.z = 0.4999999999999918
    # fr_wheel_tf.transform.rotation.w = -0.5000000000000082
    fr_wheel_tf.transform.rotation.x = 0.0
    fr_wheel_tf.transform.rotation.y = 0.0
    fr_wheel_tf.transform.rotation.z = 0.0
    fr_wheel_tf.transform.rotation.w = 1.0

    # Store all transforms in a list

    static_transforms = [
        # body_assembly_tf, # Artifact from onshape-to-urdf
        bl_tire_tf,
        br_tire_tf,
        fl_tire_tf,
        fr_tire_tf,
        vicon_ball_tf,
        bl_wheel_tf,
        br_wheel_tf,
        fl_wheel_tf,
        fr_wheel_tf,
    ]
    tf_message = TFMessage()
    tf_message._transforms = static_transforms
    return tf_message
