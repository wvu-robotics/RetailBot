import os
import shutil

def find_matching_pngs(folder_path, substrings):
    """
    Find PNG files in the given folder that contain any of the specified substrings.
    
    Args:
        folder_path (str): The directory to search for PNG files.
        substrings (list of str): List of substrings to match filenames.

    Returns:
        list of str: Full paths of matching PNG files.
    """
    matching_files = []
    
    # Ensure folder exists
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    # Iterate through files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith(".png") and any(sub in filename for sub in substrings):
            full_path = os.path.join(folder_path, filename)
            matching_files.append(full_path)
    
    return matching_files

def copy_selected_plots(src_folder, dst_folder, substrings):
    """
    Copies PNG files matching substrings from the source folder to the destination.

    Args:
        src_folder (str): The directory containing PNG files.
        dst_folder (str): The directory where selected plots should be copied.
        substrings (list of str): List of substrings to match filenames.
    """
    # Get matching PNGs
    matching_files = find_matching_pngs(src_folder, substrings)
    
    if not matching_files:
        print("No matching plots found.")
        return

    # Create destination folder if it doesn't exist
    os.makedirs(dst_folder, exist_ok=True)

    # Copy files
    for file_path in matching_files:
        shutil.copy(file_path, dst_folder)
        print(f"Copied: {file_path} -> {dst_folder}")


folder_paths =[
'figures/2025_3_11__15_49_15RPM20_con.bag',
'figures/2025_3_11__15_36_11RPM30_con.bag',
'figures/2025_3_11__15_34_08RPM60_con.bag',
'figures/2025_3_11__15_30_37RPM20_left_con_right_vinyl.bag',
'figures/2025_3_11__15_27_48RPM20_Vinyl.bag',
'figures/2025_3_11__15_25_25RPM60_Vinyl.bag',
'figures/2025_2_16__17_14_4760RPM_vinyl_linear_skid.bag',

'figures/2025_02_20__15_51_58_drive_straight_AngVel3_Distance5_conR&nylL.bag',
'figures/2025_02_20__15_40_49_arc_drive_Arclength10_ArcVel5.bag',
'figures/2025_02_20__15_45_30_arc_drive_Arclength10_ArcVel5.bag',
'figures/2025_02_20__13_14_56_drive_straight_AngularV2_Distance2_concrete..bag',
'figures/2025_02_20__11_55_32_drive_straight_AngularV2_Distance2_concrete..bag',
'figures/2025_02_20__11_54_50_drive_straight_AngularV2_Distance2_concrete.bag',
'figures/2025_2_16__17_14_4760RPM_vinyl_linear_skid.bag',
]
# Example usage
if __name__ == "__main__":
    os.makedirs("figures/selected_figures/", exist_ok=True)

    # folder_path = "figures/2025_2_16__17_14_4760RPM_vinyl_linear_skid.bag"
    for folder_path in folder_paths:
        folder_name = folder_path.split('/')[-1]
        substrings = [
            'Longitudinal_Wheel_Slip_Ratios__', 
            "Motor_Currents_vs_Slip_with_Best-Fit_Lines__",
            'Average_Motor_Currents_vs_Slip_with_Best-Fit_Line__',
            'Vicon_Marker_Linear_Vel__',
            'LOCAL_vs_VICON_Marker_TRUE_TWIST__'
            'Local_Frame_True_fl_tire_Twist',
            'Wheel_Velocities__Odom_vs_True__Filtered_for_Movement___',
            ]

        dst_folder = "figures/selected_figures/" + "selected_plots" + folder_name

        copy_selected_plots(folder_path, dst_folder, substrings)
