# Make a function for a differential drive model
from typing import Any, TypedDict
import numpy as np
import math
from numpy.typing import NDArray
from diff_drive_utils import DiffDriveState

class DiffDriveParams(TypedDict):
    r: float
    b: float


class WheelSpeeds(TypedDict):
    omega_l: float
    omega_r: float



state: DiffDriveState = DiffDriveState(np.zeros((3, 100)))

def diff_drive(
    time: float,
    state: NDArray[np.float64],
    omega_l: float,
    omega_r: float,
    r: float,
    b: float,
) -> NDArray:
    """foo!

    :param state: X, Y, Theta
    :param time: Current time
    :param omega_l: _description_
    :param omega_r: _description_
    :param r: _description_
    :param b: _description_
    :return: _description_
    """
    x, y, theta = state

    # CALCULATED INTERMEDIATES:
    v_l = r * omega_l
    v_r = r * omega_r

    # Calc body frame velocities.
    Vx = (v_l + v_r) / 2
    theta_prime = (v_r - v_l) / b

    # Transform to world frame.
    x_prime = Vx * math.cos(theta)
    y_prime = Vx * math.sin(theta)

    # Return state_prime
    return np.array([x_prime, y_prime, theta_prime])