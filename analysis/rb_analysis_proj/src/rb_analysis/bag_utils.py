import os
from datetime import datetime
from pathlib import Path

import rosbag2_py
from pandas import DataFrame
from rclpy.serialization import deserialize_message
from rosbag2_py._storage import BagMetadata
from rosidl_runtime_py.utilities import get_message

from . import bag_utils


def get_metadata(input_bag: str) -> BagMetadata:
    """Given a str file path to a MCAP rosbag return a BagMetaData obj. Add
    typing here to get attribute hints.

    We can use this to get the number of messages per topic. From rosbag2_py docs.
    """
    reader = rosbag2_py.SequentialReader()
    reader.open(
        rosbag2_py.StorageOptions(uri=input_bag, storage_id="mcap"),
        rosbag2_py.ConverterOptions(
            input_serialization_format="cdr", output_serialization_format="cdr"
        ),
    )
    return reader.get_metadata()


def get_reader(input_bag: str):
    """Yields topic, msg, timestamp. From rosbag2_py docs."""
    reader = rosbag2_py.SequentialReader()
    reader.open(
        rosbag2_py.StorageOptions(uri=input_bag, storage_id="mcap"),
        rosbag2_py.ConverterOptions(
            input_serialization_format="cdr", output_serialization_format="cdr"
        ),
    )

    topic_types = reader.get_all_topics_and_types()

    def typename(topic_name):
        for topic_type in topic_types:
            if topic_type.name == topic_name:
                return topic_type.type
        raise ValueError(f"topic {topic_name} not in bag")

    while reader.has_next():
        topic, data, timestamp = reader.read_next()
        msg_type = get_message(typename(topic))
        msg = deserialize_message(data, msg_type)
        yield topic, msg, timestamp
    del reader


def read_bag(bag_path: Path) -> dict[str, list[type]]:
    """Open a bag file given by the path and convert to a lists of message objects.
    Args:
        input_bag: Path object pointing to the ros2bag. Expects MCAP format.

    Returns:
        dict[str, list[type]]: {topic_name: [messages]}
    """
    print(os.getcwd())
    print(str(bag_path))
    meta_data = get_metadata(input_bag=str(bag_path))
    reader = get_reader(input_bag=str(bag_path))

    # Create a dict of lists with keys matching the the topic names.
    msgs = {k.topic_metadata.name: [] for k in meta_data.topics_with_message_count}

    # Use our rosbag2_py wrapper function to populate lists with corresponding messages.
    for topic, msg, timestamp in reader:
        msgs[topic].append(msg)

    return msgs


def msgs_to_df(data: dict[str, list[type]]) -> dict[str, list[DataFrame]]:
    """Open a bag file given by the path and convert to DataFrame representations.

    This function uses the automated message unpacking for compatible types. For
    special topics like tf and tf_static we use specific functions.

    Returns:
        dict[str, list[type]]: {topic_name: [DataFrame]}
    """
    ...
