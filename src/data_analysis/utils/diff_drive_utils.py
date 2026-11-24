from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from numpy.typing import NDArray


@dataclass
class DiffDriveState:
    """
    Differential Drive State.
    
    >>> state = DiffDriveState()
    >>>

    Attributes:
        state (NDArray): (3, N) array storing [x, y, theta] states over time.
        x (NDArray): View into `state[0, :]`, representing x displacement.
        y (NDArray): View into `state[1, :]`, representing y displacement.
        theta (NDArray): View into `state[2, :]`, representing orientation.
    """

    state: NDArray = field(default_factory=lambda: np.zeros((3, 1)))

    @property
    def x(self) -> NDArray:
        return self.state[0, :]

    @property
    def y(self) -> NDArray:
        return self.state[1, :]

    @property
    def theta(self) -> NDArray:
        return self.state[2, :]

    def append_state(self, new_x: float, new_y: float, new_theta: float):
        """Append a new state to the state matrix."""
        new_state = np.array([[new_x], [new_y], [new_theta]])  # Shape (3,1)
        self.state = np.hstack((self.state, new_state))  # Expand state over time

    # def __array__(self):
    #     return self.state

    def __getitem__(self, index):
        """Allow subscripting: state[i] will return state.state[i]"""
        return self.state[index]

    def __setitem__(self, index, value):
        """Allow assignment to state matrix."""
        self.state[index] = value




# Can actually skip using this for the longitudinal case.
def diff_drive(df: pd.DataFrame, r: float, b: float) -> pd.DataFrame:
    """
    Compute differential drive kinematics using a DataFrame of wheel angular velocities.

    Parameters:
        df (pd.DataFrame): DataFrame with time-indexed wheel angular velocities.
        r (float): Wheel radius.
        b (float): Distance between wheels (track width).

    Returns:
        pd.DataFrame: DataFrame containing computed body positions (x, y, theta).
    """

    # Ensure index is a DatetimeIndex for time-based calculations
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(
            "DataFrame index must be a DatetimeIndex for time-based integration."
        )

    # Extract time in seconds from index
    time = df.index.astype(np.int64) / 1e9  # Convert nanoseconds to seconds
    dt = np.diff(time, prepend=time[0])  # Compute time differences

    # Ensure required columns exist
    # required_cols = [
    #     "joint.fr_wheel_joint.angular_vel",
    #     "joint.br_wheel_joint.angular_vel",
    #     "joint.fl_wheel_joint.angular_vel",
    #     "joint.bl_wheel_joint.angular_vel"
    # ]
    required_cols = [
        "joint.fr_wheel_joint.velocity",
        "joint.br_wheel_joint.velocity",
        "joint.fl_wheel_joint.velocity",
        "joint.bl_wheel_joint.velocity",
    ]
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"DataFrame must contain columns: {required_cols}")

    # Compute averaged left and right wheel angular velocities
    omega_l = (
        df["joint.fl_wheel_joint.velocity"] + df["joint.bl_wheel_joint.velocity"]
    ) / 2
    omega_r = (
        df["joint.fr_wheel_joint.velocity"] + df["joint.br_wheel_joint.velocity"]
    ) / 2

    # Convert wheel angular velocities to linear velocities
    v_l = r * omega_l
    v_r = r * omega_r

    # Compute body frame velocities
    Vx = (v_l + v_r) / 2  # Linear velocity
    theta_prime = (v_r - v_l) / b  # Angular velocity

    # Compute world-frame position updates
    x_prime = Vx * np.cos(theta_prime) * dt
    y_prime = Vx * np.sin(theta_prime) * dt
    theta = np.cumsum(theta_prime * dt)  # Integrate angular velocity

    # Compute absolute world positions by integrating velocity over time
    x = np.cumsum(x_prime)
    y = np.cumsum(y_prime)

    # Return computed position as a DataFrame
    return pd.DataFrame({"x": x, "y": y, "theta": theta}, index=df.index)











if __name__ == "__main__":
    import doctest

    doctest.testmod()


