import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
from pathlib import Path
from collections import namedtuple



def plot_currents(
    data: pd.DataFrame, metadata: dict, title: str = "", save=True, show: bool = False
) -> Figure:
    data.plot(
        title=f"{title}\n{metadata['plot_subtitle']}",
        xlabel="Seconds",
        ylabel="Current (Amps)",
        subplots=True,
        grid=True,
        figsize=(16,6),
    )
    fig = plt.gcf()
    if save:
        out_dir = Path(metadata["artifact_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)

        fname = out_dir / f"{title}.png"

        fig.savefig(str(fname), dpi=300, bbox_inches="tight")

    if not show:
        plt.close(fig)
    return fig


def plot_encoder_counts(
    data: pd.DataFrame, metadata: dict, title: str = "", save=True, show: bool = False
) -> Figure:
    data.plot(
        title=f"{title}\n{metadata['plot_subtitle']}",
        xlabel="Seconds",
        ylabel="Counts",
        subplots=True,
        grid=True,
        
    )
    fig = plt.gcf()
    if save:
        out_dir = Path(metadata["artifact_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)

        fname = out_dir / f"{title}.png"

        fig.savefig(str(fname), dpi=300, bbox_inches="tight")

    if not show:
        plt.close(fig)
    return fig


def plot_pose(
    data: pd.DataFrame, metadata: dict, title: str = "", save=True, show: bool = False
) -> Figure:
    data.plot(
        title=f"{title}\n{metadata['plot_subtitle']}",
        xlabel="Seconds",
        ylabel="m or quat",
        subplots=True,
        grid=True,
    )

    fig = plt.gcf()
    if save:
        # Set, possibly create dir, and save as png.
        out_dir = Path(metadata["artifact_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)
        fname = out_dir / f"{title}.png"
        fig.savefig(str(fname), dpi=300, bbox_inches="tight")

    if not show:
        plt.close(fig)
    return fig

def plot_twist(
    data: pd.DataFrame, metadata: dict, title: str = "", save=True, show: bool = False
) -> Figure:
    data.plot(
        title=f"{title}\n{metadata['plot_subtitle']}",
        figsize=(9,9),
        xlabel="Seconds",
        ylabel="m or quat",
        subplots=True,
        grid=True,
    )

    fig = plt.gcf()
    if save:
        # Set, possibly create dir, and save as png.
        out_dir = Path(metadata["artifact_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)
        fname = out_dir / f"{title}.png"
        fig.savefig(str(fname), dpi=300, bbox_inches="tight")

    if not show:
        plt.close(fig)
    return fig

def generic_plot(
    data: pd.DataFrame, metadata: dict, title: str = "", save=True, show: bool = False
) -> Figure:
    data.plot(
        title=f"{title}\n{metadata['plot_subtitle']}",
        xlabel="Seconds",
        ylabel="Counts",
        subplots=True,
        grid=True,
    )
    fig = plt.gcf()
    if save:
        out_dir = Path(metadata["artifact_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)

        fname = out_dir / f"{title}.png"

        fig.savefig(str(fname), dpi=300, bbox_inches="tight")

    if not show:
        plt.close(fig)
    return fig


# This is clever.
# Define a simple container for plot settings
PlotSpec = namedtuple("PlotSpec", ["columns", "plot_kwargs"])

# For each topic, specify which columns to plot and any custom kwargs
plot_specs = {
    "left_motor_torques": PlotSpec(
        columns=["left_front_torque", "left_back_torque"],
        plot_kwargs={"title": "Left Motor Torques", "xlabel": "Time (s)", "ylabel": "Torque (Nm)", "grid": True},
    ),
    "right_motor_torques": PlotSpec(
        columns=["right_front_torque", "right_back_torque"],
        plot_kwargs={"title": "Right Motor Torques", "xlabel": "Time (s)", "ylabel": "Torque (Nm)", "grid": True},
    ),

}

