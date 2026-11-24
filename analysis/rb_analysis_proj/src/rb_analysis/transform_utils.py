import numpy as np
import pandas as pd
import PyKDL as kdl
from scipy.spatial.transform import Rotation


def compute_vicon_twist(
    df_pose: pd.DataFrame,
    time_cols: tuple = ("sec", "nanosec"),
    pos_cols: tuple = ("x", "y", "z"),
    quat_cols: tuple = ("qx", "qy", "qz", "qw"),
    timestamp_at: str = "end",  # "start", "end", or "mid"
) -> pd.DataFrame:
    """
    From PoseStamped in the vicon frame, compute:
      vx, vy, vz, wx, wy, wz
    and return a DataFrame of length N-1 whose index is drawn
    from df_pose.index (later samples if timestamp_at="end").
    """
    # 1. continuous time in seconds
    t = df_pose[time_cols[0]] + df_pose[time_cols[1]] * 1e-9
    dt = np.diff(t.values)  # length N-1

    # 2. linear velocities in vicon frame
    pos = df_pose[list(pos_cols)].to_numpy()
    v = np.diff(pos, axis=0) / dt[:, None]

    # 3. angular velocities in vicon frame
    rots = Rotation.from_quat(df_pose[list(quat_cols)].to_numpy())
    ang = []
    for i in range(len(rots) - 1):
        R_rel = rots[i + 1].as_matrix() @ rots[i].as_matrix().T
        ang.append(Rotation.from_matrix(R_rel).as_rotvec() / dt[i])
    ang = np.vstack(ang)

    # 4. pick output index
    if timestamp_at == "start":
        idx = df_pose.index[:-1]
    elif timestamp_at == "mid":
        # average of two timestamps
        idx = df_pose.index[:-1] + (df_pose.index[1:] - df_pose.index[:-1]) / 2
    else:  # "end"
        idx = df_pose.index[1:]

    # 5. assemble DataFrame, preserve index
    out = pd.DataFrame(
        {
            "vx": v[:, 0],
            "vy": v[:, 1],
            "vz": v[:, 2],
            "wx": ang[:, 0],
            "wy": ang[:, 1],
            "wz": ang[:, 2],
        },
        index=idx,
    )

    return out


def compute_body_twist(
    df_vicon_twist: pd.DataFrame,
    df_pose: pd.DataFrame,
    quat_cols: tuple = ("qx", "qy", "qz", "qw"),
) -> pd.DataFrame:
    """
    Rotate vicon‐frame twist into body frame.
    Assumes df_vicon_twist.index ⊆ df_pose.index.
    """
    # grab quaternions at exactly the same timestamps
    q = df_pose.loc[df_vicon_twist.index, list(quat_cols)].to_numpy()
    Rs = Rotation.from_quat(q)
    Rinv = Rs.inv().as_matrix()  # (M,3,3)

    # slice out vicon‐frame velocities
    v_v = df_vicon_twist[["vx", "vy", "vz"]].to_numpy()
    w_v = df_vicon_twist[["wx", "wy", "wz"]].to_numpy()

    # rotate into body frame
    v_b = np.einsum("kij,kj->ki", Rinv, v_v)
    w_b = np.einsum("kij,kj->ki", Rinv, w_v)

    return pd.DataFrame(
        {
            "vx": v_b[:, 0],
            "vy": v_b[:, 1],
            "vz": v_b[:, 2],
            "wx": w_b[:, 0],
            "wy": w_b[:, 1],
            "wz": w_b[:, 2],
        },
        index=df_vicon_twist.index,
    )


def transform_twist_displacement(
    df_twist: pd.DataFrame,
    translation: np.ndarray,
    quaternion: np.ndarray | None = None,
    rotation_matrix: np.ndarray | None = None,
    v_dims: tuple = ("vx_b", "vy_b", "vz_b"),
    w_dims: tuple = ("wx_b", "wy_b", "wz_b"),
    out_prefix: str = "",
) -> pd.DataFrame:
    """
    Rigid‐body displacement of a twist:
      v_child = R @ v_parent + skew(p) @ (R @ w_parent)
      w_child = R @ w_parent
    """
    if rotation_matrix is None:
        if quaternion is None:
            raise ValueError("Provide quaternion or rotation_matrix")
        R = Rotation.from_quat(quaternion).as_matrix()
    else:
        R = rotation_matrix

    p = translation
    skew_p = np.array([[0, -p[2], p[1]], [p[2], 0, -p[0]], [-p[1], p[0], 0]])
    skewR = skew_p @ R

    V = df_twist[list(v_dims)].to_numpy()  # (N,3)
    W = df_twist[list(w_dims)].to_numpy()  # (N,3)

    V_child = (R @ V.T).T + (skewR @ W.T).T
    W_child = (R @ W.T).T

    data = {}
    for i, name in enumerate(v_dims):
        data[out_prefix + name] = V_child[:, i]
    for i, name in enumerate(w_dims):
        data[out_prefix + name] = W_child[:, i]

    return pd.DataFrame(data, index=df_twist.index)


def df_static_to_kdl_transforms(df_static: pd.DataFrame) -> dict:
    """
    Convert a tf_static DataFrame into a dict of PyKDL Frames.
    Returns: {(parent, child): kdl.Frame}
    """
    transforms = {}
    for _, row in df_static.iterrows():
        parent = row["header._frame_id"]
        child = row["_child_frame_id"]
        # translation
        p = kdl.Vector(
            row["transform.translation.x"],
            row["transform.translation.y"],
            row["transform.translation.z"],
        )
        # rotation
        qx, qy, qz, qw = (
            row["transform.rotation.x"],
            row["transform.rotation.y"],
            row["transform.rotation.z"],
            row["transform.rotation.w"],
        )
        R = kdl.Rotation.Quaternion(qx, qy, qz, qw)
        transforms[(parent, child)] = kdl.Frame(R, p)
    return transforms


def get_kdl_chain(transforms: dict, source: str, target: str) -> kdl.Frame:
    """
    Compose the KDL Frames along the unique path from source→target.
    Raises KeyError if no path exists.
    """
    # build adjacency lists
    adj = {}
    for (p, c), frame in transforms.items():
        adj.setdefault(p, []).append((c, frame, False))
        adj.setdefault(c, []).append((p, frame, True))  # True means invert

    # DFS to find path
    visited = set()
    path = []

    def dfs(curr):
        if curr == target:
            return True
        visited.add(curr)
        for nbr, frame, inv in adj.get(curr, []):
            if nbr in visited:
                continue
            path.append((nbr, frame, inv))
            if dfs(nbr):
                return True
            path.pop()
        return False

    if not dfs(source):
        raise KeyError(f"No transform path from {source} to {target}")

    # chain transforms
    T = kdl.Frame()  # identity
    prev = source
    for nbr, frame, inv in path:
        if inv:
            T = T * transforms[(nbr, prev)].Inverse()
        else:
            T = T * transforms[(prev, nbr)]
        prev = nbr
    return T


def transform_twist_with_kdl(
    df_twist: pd.DataFrame,
    kdl_frame: kdl.Frame,
    v_dims: tuple = ("vx", "vy", "vz"),
    w_dims: tuple = ("wx", "wy", "wz_b"),
    out_prefix: str = "",
) -> pd.DataFrame:
    """
    Displace each twist by a PyKDL.Frame:
      [v'; ω'] = Ad_F * [v; ω], where Ad_F = [R  skew(p)R; 0  R].
    """
    rows = []
    for ts, row in df_twist.iterrows():
        # build KDL twist
        v = kdl.Vector(row[v_dims[0]], row[v_dims[1]], row[v_dims[2]])
        w = kdl.Vector(row[w_dims[0]], row[w_dims[1]], row[w_dims[2]])
        twist = kdl.Twist(v, w)
        # apply displacement
        new_twist = kdl_frame * twist
        vel = new_twist.vel
        rot = new_twist.rot
        rows.append([vel[0], vel[1], vel[2], rot[0], rot[1], rot[2]])

    cols = [out_prefix + n for n in (*v_dims, *w_dims)]
    return pd.DataFrame(rows, index=df_twist.index, columns=cols)


# def transform_twist_displacement_only(
#     df_twist: pd.DataFrame,
#     static_frame: kdl.Frame,
#     v_dims: tuple = ("vx", "vy", "vz"),
#     w_dims: tuple = ("wx", "wy", "wz"),
#     out_prefix: str = "",
# ) -> pd.DataFrame:
#     """
#     Apply translation-only adjoint to each twist:
#       ω' = ω
#       v' = v + ω × p
#     where p = static_frame.p is given in the marker frame.
#     """
#     p = static_frame.p
#     rows = []
#     for _, row in df_twist.iterrows():
#         v = kdl.Vector(row[v_dims[0]], row[v_dims[1]], row[v_dims[2]])
#         w = kdl.Vector(row[w_dims[0]], row[w_dims[1]], row[w_dims[2]])
#         omega_prime = w
#         v_prime = v + w*p
#         rows.append(
#             [v_prime[0], v_prime[1], v_prime[2], omega_prime[0], omega_prime[1], omega_prime[2]]
#         )
#     cols = [out_prefix + n for n in (*v_dims, *w_dims)]
#     return pd.DataFrame(rows, index=df_twist.index, columns=cols)

# def transform_twist_displacement_only(
#     df_twist: pd.DataFrame,
#     df_pose: pd.DataFrame,
#     static_frame: kdl.Frame,
#     v_dims=("vx","vy","vz"),
#     w_dims=("wx","wy","wz"),
#     out_prefix=""
# ) -> pd.DataFrame:
#     rows = []
#     for t, row in df_twist.iterrows():
#         # rotate p into Vicon axes
#         pose = df_pose.loc[t]
#         R_vm = kdl.Rotation.Quaternion(
#             pose["qx"], pose["qy"], pose["qz"], pose["qw"]
#         )
#         p_vicon = R_vm * static_frame.p

#         v = kdl.Vector(row[v_dims[0]], row[v_dims[1]], row[v_dims[2]])
#         w = kdl.Vector(row[w_dims[0]], row[w_dims[1]], row[w_dims[2]])

#         omega_prime = w
#         v_prime = v + (w * p_vicon)

#         rows.append([
#             v_prime[0], v_prime[1], v_prime[2],
#             omega_prime[0], omega_prime[1], omega_prime[2],
#         ])

#     cols = [out_prefix + n for n in (*v_dims, *w_dims)]
#     return pd.DataFrame(rows, index=df_twist.index, columns=cols)


def transform_twist_displacement_only(
    df_twist: pd.DataFrame,
    df_pose: pd.DataFrame,
    static_frame: kdl.Frame,
    v_dims=("vx", "vy", "vz"),
    w_dims=("wx", "wy", "wz"),
    out_prefix="",
) -> pd.DataFrame:
    # Record twist timestamps
    twist_t = df_twist.index.to_numpy()

    # Find nearest timestamps in df_pose
    pose_t = df_pose.index.to_numpy()
    idx_pose_nearest = np.searchsorted(pose_t, twist_t, side="left")

    # Clamp edge cases
    idx_pose_nearest[idx_pose_nearest == len(pose_t)] = len(pose_t) - 1

    # Handle potential off-by-one better: compare to left neighbor too
    left_idx = np.clip(idx_pose_nearest - 1, 0, len(pose_t) - 1)
    right_idx = idx_pose_nearest
    left_dt = np.abs(twist_t - pose_t[left_idx])
    right_dt = np.abs(twist_t - pose_t[right_idx])
    use_right = right_dt < left_dt
    chosen_idx = np.where(use_right, right_idx, left_idx)
    matched_pose_times = pose_t[chosen_idx]

    # Print diagnostics
    exact_matches = np.sum(matched_pose_times == twist_t)
    print(f"[Transform] Exact timestamp matches: {exact_matches} / {len(twist_t)}")
    print(f"[Transform] Mean Δt: {np.mean(np.abs(matched_pose_times - twist_t)):.6f} s")
    print(f"[Transform] Max  Δt:  {np.max(np.abs(matched_pose_times - twist_t)):.6f} s")

    # Align poses
    df_pose_aligned = df_pose.loc[matched_pose_times]
    df_pose_aligned.index = df_twist.index  # force same index

    if df_pose_aligned.isna().any().any():
        print("[Transform] WARNING: Pose alignment produced NaNs!")

    # ---- Transform ----
    rows = []
    for t, row in df_twist.iterrows():
        pose = df_pose_aligned.loc[t]

        R_vm = kdl.Rotation.Quaternion(pose["qx"], pose["qy"], pose["qz"], pose["qw"])
        p_vicon = R_vm * static_frame.p

        v = kdl.Vector(row[v_dims[0]], row[v_dims[1]], row[v_dims[2]])
        w = kdl.Vector(row[w_dims[0]], row[w_dims[1]], row[w_dims[2]])

        omega_prime = w
        v_prime = v + (w * p_vicon)

        rows.append(
            [
                v_prime[0],
                v_prime[1],
                v_prime[2],
                omega_prime[0],
                omega_prime[1],
                omega_prime[2],
            ]
        )

    cols = [out_prefix + n for n in (*v_dims, *w_dims)]
    return pd.DataFrame(rows, index=df_twist.index, columns=cols)
