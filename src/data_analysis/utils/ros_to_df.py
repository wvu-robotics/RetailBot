from typing import List, Union, Any, Optional
import pandas as pd
from pandas import DataFrame
import array


def ros_message_to_df(
    messages: Union[Any, List[Any]], fields: Optional[List[str]] = None
) -> DataFrame:
    """
    Convert a ROS 2 message (or a list of messages) into a Pandas DataFrame.

    - Extracts all numeric fields from the message.
    - Recursively flattens nested structures.
    - Uses timestamp from 'header.stamp' as index if available.
    - Allows filtering specific fields using dot notation (e.g., 'pose.position.x').

    :param messages: A single ROS message or a list of ROS messages.
    :param fields: A list of field names to keep. If None, keeps all fields.
    :return: Pandas DataFrame with extracted fields.
    """
    if not isinstance(messages, list):
        messages = [messages]  # Convert single message to list

    # Extract data
    data = []
    indices = []

    for msg in messages:
        if hasattr(msg, "joint_names") and hasattr(msg, "interface_values"):
            msg_dict = flatten_dynamic_joint_state(msg)
        else:
            msg_dict = flatten_ros_message(msg)

        msg_dict = {k: v for k, v in msg_dict.items() if not k.endswith("check_fields")}

        timestamp = None
        if hasattr(msg, "header") and hasattr(msg.header, "stamp"):
            timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
            indices.append(timestamp)

        data.append(msg_dict)

    # Create DataFrame
    df = pd.DataFrame(data)

    if df.empty:
        raise ValueError("No valid data extracted from messages.")

    # Convert requested dot notation fields into the flattened keys
    if fields is not None:
        # flattened_keys = [field.replace(".", "_") for field in fields]
        # flattened_keys = fields

        # Check for missing fields
        missing_fields = [col for col in fields if col not in df.columns]
        if missing_fields:
            raise KeyError(
                f"Requested fields {missing_fields} not found. Available fields: {list(df.columns)}"
            )

        df = df[fields]

        # Rename back from underscores to dot notation for clarity
        df.columns = fields

    # Set index as timestamp if available
    if indices:
        df.index = pd.to_datetime(indices, unit="s")
        df.index.name = "timestamp"

    return df


def flatten_ros_message(msg: Any, prefix: str = "") -> dict:
    """
    Recursively flatten a ROS message into a dictionary, using dot notation
    while removing private underscores.

    - Keeps string fields (e.g., child_frame_id) as-is.
    - Uses dot notation only for nested ROS messages.

    :param msg: ROS message instance.
    :param prefix: Prefix for nested field names.
    :return: Dictionary of flattened fields.
    """
    result = {}

    # If it's a simple data type (int, float, str, bool), return as-is
    if isinstance(msg, (int, float, bool, str)):
        return {prefix.rstrip("."): msg}  # Keep string fields without dot notation

    # If it's a ROS message (has __slots__), recursively extract attributes
    if hasattr(msg, "__slots__"):
        for attr in msg.__slots__:
            value = getattr(msg, attr)

            # Keep child_frame_id as-is (do not flatten)
            if isinstance(value, str):
                # if value == 'check_fields':
                #     continue
                result[f"{prefix}{attr}"] = value
                continue

            # Remove leading underscores from attribute names
            clean_attr = attr.lstrip("_")
            key = f"{prefix}{clean_attr}."  # Use dot notation
            # Expand float arrays into separate indexed columns

            # Handle float64[] arrays and array.array
            if isinstance(value, (list, array.array)) and all(
                isinstance(i, (int, float)) for i in value
            ):
                for i, v in enumerate(value):
                    result[f"{key}{i}"] = v  # Example: "data_0", "data_1"
            else:
                result.update(flatten_ros_message(value, key))

    return result


def flatten_dynamic_joint_state(msg: Any) -> dict:
    """
    Flatten a `DynamicJointState` message into a dictionary using dot notation.

    - Expands `joint_names` into a structured format.
    - Extracts `interface_values` for each joint.
    - Uses dot notation (e.g., `joint.br_wheel_joint.velocity` instead of underscores).

    :param msg: The `DynamicJointState` message.
    :return: Dictionary of expanded fields.
    """
    result = {}

    if not hasattr(msg, "joint_names") or not hasattr(msg, "interface_values"):
        return result

    joint_names = msg.joint_names  # List of joint names
    interface_values = msg.interface_values  # List of InterfaceValue messages

    if len(joint_names) != len(interface_values):
        raise ValueError(
            f"Mismatch: {len(joint_names)} joint names but {len(interface_values)} interface value lists."
        )

    for joint_idx, joint_name in enumerate(joint_names):
        joint_interfaces = interface_values[joint_idx]  # Get the corresponding interface values

        if hasattr(joint_interfaces, "values") and hasattr(joint_interfaces, "interface_names"):
            for i, interface_name in enumerate(joint_interfaces.interface_names):
                key = f"joint.{joint_name}.{interface_name}"  # Use dot notation
                result[key] = (
                    joint_interfaces.values[i] if i < len(joint_interfaces.values) else None
                )

    return result
