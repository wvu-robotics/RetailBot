import os
from glob import glob
from setuptools import setup

package_name = "rb_bringup"


def files(path):
    return [f for f in glob(path, recursive=True) if os.path.isfile(f)]

setup(
    name=package_name,
    version="0.0.0",
    packages=[package_name],
    py_modules=["scripts.encoder_current_monitor"],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", files("launch/*")),
        (f"share/{package_name}/config", files('config/*')),
        # (f"share/{package_name}/config/teleop_configs", files('config/teleop_configs/*')),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="devuser",
    maintainer_email="devuser@todo.todo",
    description="TODO: Package description",
    license="TODO: License declaration",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "encoder_current_monitor = scripts.encoder_current_monitor:main",
        ],
    },
)
