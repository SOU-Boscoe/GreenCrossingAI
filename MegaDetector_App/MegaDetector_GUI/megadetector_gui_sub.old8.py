import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import subprocess
import os
# importing video processing methods from video_utils file.
import sys
#video_utils_path = '/shared/land_bridge/MegaDetector_App/MegaDetector/detection'
#sys.path.append(video_utils_path)
#import video_utils

def browse_path(entry, is_file=False):
    if is_file:
        selected = filedialog.askopenfilename()  # For selecting a single file
    else:
        selected = filedialog.askdirectory()  # For selecting a directory
    entry.delete(0, tk.END)
    entry.insert(0, selected)

def run_command(command, env, log_file_path):
    with open(log_file_path, 'a') as log_file:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, bufsize=1, universal_newlines=True)
        for line in process.stdout:
            log_file.write(line)
            text_response.insert(tk.END, line)
            text_response.see(tk.END)
            root.update_idletasks()
        process.stdout.close()
        process.wait()

def run_commands_thread():
    base_image_folder = entry_image_folder.get()
    output_directory = os.path.join(entry_output_directory.get(), os.path.basename(base_image_folder) + "_results")
    os.makedirs(output_directory, exist_ok=True)

    log_file_path = os.path.join(output_directory, "command_output.log")

    python_executable = "python"
    model_path = entry_model_path.get() or "MDV5A"

    env = os.environ.copy()
    
    # Checking for video file 
    
   # video_files = video_utils.find_videos(base_image_folder, recursive=True)
   # if video_files:
   # 	for video_file in video_files:
   # 		video_output_dir = os.path.join(output_directory, os.path.splitext(os.path.basename(video_file))[0])
   # 		os.makedirs(video_output_dir, exist_ok=True)
   # 		frame_output_dir = os.path.join(video_output_dir, 'frames')
   # 		os.makedirs(frame_output_dir, exist_ok=True)
   # 		frames, fps = video_utils.video_to_frames(video_file, frame_output_dir, verbose=True)
   # 		for frame in frames:
   # 			json_output_path = os.path.join(frame_output_dir, os.path.basename(frame) + ".json")
   # 			frame_cmd = f'{python_executable} /shared/land_bridge/MegaDetector_App/MegaDetector/detection/run_detector_batch.py "{model_path}" "{frame_output_dir}" "{json_output_path}" --output_relative_filenames --recursive --checkpoint_frequency 1000 --quiet'
   # 			run_command(frame_cmd, env, log_file_path)
    

    for subdir in os.listdir(base_image_folder):
        subdir_path = os.path.join(base_image_folder, subdir)
        if os.path.isdir(subdir_path):
            subdir_output_path = os.path.join(output_directory, subdir)
            os.makedirs(subdir_output_path, exist_ok=True)
            json_output_path = os.path.join(subdir_output_path, subdir + ".json")

            commands = [
                f'{python_executable} /shared/land_bridge/MegaDetector_App/MegaDetector/detection/run_detector_batch.py "{model_path}" "{subdir_path}" "{json_output_path}" --output_relative_filenames --recursive --checkpoint_frequency 1000 --quiet',
                f'{python_executable} /shared/land_bridge/MegaDetector_App/MegaDetector/api/batch_processing/postprocessing/postprocess_batch_results.py "{json_output_path}" "{subdir_output_path}" --image_base_dir "{subdir_path}" --num_images_to_sample -1'
            ]

            for command in commands:
                run_command(command, env, log_file_path)
    os.system(f'xdg-open "{output_directory}"')  # Open the directory after command completion

def run_single_image_command():
    image_file_path = entry_single_image_file.get()
    log_file_path = "single_image_process.log"

    python_executable = "python"
    model_path = entry_model_path.get() or "MDV5A"

    command = f'{python_executable} /shared/land_bridge/MegaDetector_App/MegaDetector/detection/run_detector.py "{model_path}" --image_file "{image_file_path}" --threshold 0.1'
    run_command(command, env, log_file_path)
    
    image_directory = os.path.dirname(image_file_path)
    os.system(f'xdg-open "{image_directory}"') # Open the directory after command completion

root = tk.Tk()
root.title("MegaDetector Runner")

pane = tk.PanedWindow(root, orient=tk.HORIZONTAL)
pane.pack(fill=tk.BOTH, expand=1)

# Model Path Frame
model_frame = tk.Frame(pane)
pane.add(model_frame)
tk.Label(model_frame, text="Specify Model Path (optional, default is MDV5A)").pack()
entry_model_path = tk.Entry(model_frame, width=50)
entry_model_path.pack()
tk.Button(model_frame, text="Browse Model File", command=lambda: browse_path(entry_model_path, is_file=True)).pack()

# Batch Process Frame
batch_frame = tk.Frame(pane)
pane.add(batch_frame)
tk.Label(batch_frame, text="Batch Process Images").pack()
entry_image_folder = tk.Entry(batch_frame, width=50)
entry_image_folder.pack()
tk.Button(batch_frame, text="Browse Image Data Folder", command=lambda: browse_path(entry_image_folder)).pack()
entry_output_directory = tk.Entry(batch_frame, width=50)
entry_output_directory.pack()
tk.Button(batch_frame, text="Browse Output Directory", command=lambda: browse_path(entry_output_directory)).pack()
tk.Button(batch_frame, text="Run Batch", command=run_commands_thread).pack()

# Single Image Process Frame
single_frame = tk.Frame(pane)
pane.add(single_frame)
tk.Label(single_frame, text="Process Single Image").pack()
entry_single_image_file = tk.Entry(single_frame, width=50)
entry_single_image_file.pack()
tk.Button(single_frame, text="Browse Image File", command=lambda: browse_path(entry_single_image_file, is_file=True)).pack()
tk.Button(single_frame, text="Run Single", command=run_single_image_command).pack()

# Shared Terminal Output
text_response = tk.Text(root, height=15)
text_response.pack(fill=tk.BOTH, expand=True)

root.mainloop()

