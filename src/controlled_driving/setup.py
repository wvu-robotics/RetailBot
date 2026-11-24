from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'controlled_driving'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*')),
        (os.path.join('launch', package_name, 'launch'), glob('launch/*')),
        (os.path.join('config', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rb',
    maintainer_email='nep9358@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'controlled_driving = controlled_driving.controlled_driving:main',
            'slide_drive = controlled_driving.slide_drive:main',
        ],
    },
)
