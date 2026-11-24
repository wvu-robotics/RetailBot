from rclpy.serialization import deserialize_message
import rosbag2_py
from rosbag2_py._storage import BagMetadata
from rosidl_runtime_py.utilities import get_message

""" Stubs don't declare many of the return types for rosbag2_py.
"""

def get_metadata(input_bag: str) -> BagMetadata:
    """ Given a str file path to a MCAP rosbag return a BagMetaData obj. Add typing here to get attribute hints.
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
    """ Yields topic, msg, timestamp
    """    
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
