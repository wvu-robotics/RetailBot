# import os
# import papermill as pm

# def run_notebook(bag_file):
#     """Executes the Jupyter notebook with the given bag file."""
#     notebook_path = "frame_analysis.ipynb"
#     # notebook_path = ""
#     output_dir = "processed_results"  # Define an output folder
#     os.makedirs(output_dir, exist_ok=True)  # Ensure the folder exists

#     output_notebook = os.path.join(output_dir, f"processed_{os.path.basename(bag_file).replace('.bag', '')}.ipynb")

#     # output_notebook = f"processed_{bag_file.replace('.bag', '')}.ipynb"

#     pm.execute_notebook(
#         notebook_path,
#         output_notebook,
#         parameters={"bag_file": bag_file}
#     )

#     print(f"Processed {bag_file} -> {output_notebook}")

import nbformat
import os
import subprocess

import re

def preprocess_script(script_path):
    """Replaces Jupyter-specific `display()` calls with `print()` in the script."""
    with open(script_path, "r") as f:
        script_content = f.read()

    # Replace display(x) with print(x)
    script_content = re.sub(r"display\((.*?)\)", r"print(\1)", script_content)

    # Save the modified script
    modified_script_path = script_path.replace(".py", "_modified.py")
    with open(modified_script_path, "w") as f:
        f.write(script_content)

    return modified_script_path



def run_notebook(notebook_path, bag_name):
    """Executes a Jupyter notebook while dynamically setting `bag_name`."""
    
    # Ensure correct script name
    script_name = notebook_path.replace(".ipynb", ".py")
    
    # Explicitly set output filename
    subprocess.run([
        "jupyter", "nbconvert", "--to", "script",
        "--output", script_name.replace(".py", ""),  # Avoid double `.py.py`
        notebook_path
    ], check=True)
    
    # Verify if the script was created correctly
    if not os.path.exists(script_name):
        raise FileNotFoundError(f"Expected script '{script_name}' was not generated.")

    # Modify script to inject `bag_name`
    with open(script_name, "r") as f:
        lines = f.readlines()

    # Insert `bag_name` at the beginning
    new_lines = [f'bag_file = "{bag_name}"\n'] + lines

    # Write modified script
    modified_script_path = script_name.replace(".py", "_modified.py")
    with open(modified_script_path, "w") as f:
        f.writelines(new_lines)


    # Get rid of display()
    modified_script_path = preprocess_script(modified_script_path)
    # Run the modified script
    subprocess.run(["python", modified_script_path], check=True)

    # Clean up
    os.remove(script_name)
    os.remove(modified_script_path)


bag_files = [
    # 'logging/2025_2_3_rosbags/2025_2_3__16_52_49sit_still_1min.bag',
    # 'logging/2025_2_3_rosbags/2025_2_3__16_56_14imu_still_17min.bag',
    # 'logging/2025_2_3_rosbags/2025_2_3__17_25_29drive_stop_1.bag',
    # 'logging/2025_2_3_rosbags/2025_2_3__17_29_08drive_back_9prm_1.bag',
    # 'logging/2025_2_3_rosbags/2025_2_3__17_42_08spin_40s_5rpm_1.bag',
    # 'logging/2025_2_3_rosbags/2025_2_3__18_00_30sin_drive_0to6RPM.bag',

    # 'logging/2025_2_5_rosbags/2025_2_5__17_52_080.2m/sec_concrete.bag',
    # 'logging/2025_2_5_rosbags/2025_2_5__17_53_020.4m',
    # 'logging/2025_2_5_rosbags/2025_2_5__17_53_480.6m',
    # 'logging/2025_2_5_rosbags/2025_2_5__17_54_500.6m',
    # 'logging/2025_2_5_rosbags/2025_2_5__17_55_430.8m',
    # 'logging/2025_2_5_rosbags/2025_2_5__17_56_200.8m',
    # 'logging/2025_2_5_rosbags/2025_2_5__17_59_181m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_02_221.2m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_06_370.2m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_04_490.2m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_34_580.2m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_37_580.4m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_41_460.6m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_43_390.8m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_45_151m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_47_460.2m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_49_160.4m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_51_460.6m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_53_540.8m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_55_110.8m',
    # 'logging/2025_2_5_rosbags/2025_2_5__18_57_530.8m',

    'logging/2025_2_16_rosbags/2025_2_16__15_20_10RPM2.0_Vinyl.bag',
    'logging/2025_2_16_rosbags/2025_2_16__15_41_00RPM2.0_Vinyl_test.bag',
    'logging/2025_2_16_rosbags/2025_2_16__15_48_02RPM3.0_Vinyl.bag',
    'logging/2025_2_16_rosbags/2025_2_16__16_00_08RPM5.0_Vinyl.bag',
    'logging/2025_2_16_rosbags/2025_2_16__16_05_04RBM5.0_TEST.bag',
    'logging/2025_2_16_rosbags/2025_2_16__16_45_585RPM_vinyl_linear.bag',
    'logging/2025_2_16_rosbags/2025_2_16__17_14_4760RPM_vinyl_linear_skid.bag',
    'logging/2025_2_16_rosbags/2025_2_16__17_18_2110RPM_concrete_linear_skid.bag',
    'logging/2025_2_16_rosbags/2025_2_16__17_21_0660RPM_concrete_linear_skid.bag',
    'logging/2025_2_16_rosbags/2025_2_16__17_25_2230RPMback_40RPMfront.bag',
    'logging/2025_2_16_rosbags/2025_2_16__17_27_4230RPMback_50RPMfront.bag',
    'logging/2025_2_16_rosbags/2025_2_16__17_32_4930RPMback_60RPMfront.bag',
    'logging/2025_2_16_rosbags/2025_2_16__17_35_4130RPMback_60RPMfront_v2.bag',

    # 'logging/2025_2_20_rosbags/2025_02_20__11_54_50_drive_straight_AngularV2_Distance2_concrete.bag',
    # 'logging/2025_2_20_rosbags/2025_02_20__11_55_32_drive_straight_AngularV2_Distance2_concrete..bag',
    # 'logging/2025_2_20_rosbags/2025_02_20__13_14_56_drive_straight_AngularV2_Distance2_concrete..bag',
    # 'logging/2025_2_20_rosbags/2025_02_20__15_40_49_arc_drive_Arclength10_ArcVel5.bag',
    # 'logging/2025_2_20_rosbags/2025_02_20__15_45_30_arc_drive_Arclength10_ArcVel5.bag',
    # 'logging/2025_2_20_rosbags/2025_02_20__15_51_58_drive_straight_AngVel3_Distance5_conR&nylL.bag',


    # 'logging/2025_3_11_rosbags_correct/2025_3_11__15_25_25RPM60_Vinyl.bag',
    # 'logging/2025_3_11_rosbags_correct/2025_3_11__15_27_48RPM20_Vinyl.bag',
    # 'logging/2025_3_11_rosbags_correct/2025_3_11__15_30_37RPM20_left_con_right_vinyl.bag',
    # 'logging/2025_3_11_rosbags_correct/2025_3_11__15_34_08RPM60_con.bag',
    # 'logging/2025_3_11_rosbags_correct/2025_3_11__15_36_11RPM30_con.bag',
    # 'logging/2025_3_11_rosbags_correct/2025_3_11__15_49_15RPM20_con.bag'

]

for bag in bag_files:
    run_notebook("frame_analysis.ipynb", bag)


