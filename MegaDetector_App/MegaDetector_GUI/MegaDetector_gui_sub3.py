import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import subprocess
import os

def open_file_explorer(directory):
    directory = directory.replace('/', '\\')
    subprocess.Popen(['explorer', directory])

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
    class_mapping_filename = entry_class_mapping.get()

    env = os.environ.copy()

    for subdir in os.listdir(base_image_folder):
        subdir_path = os.path.join(base_image_folder, subdir)
        if os.path.isdir(subdir_path):
            subdir_output_path = os.path.join(output_directory, subdir)
            os.makedirs(subdir_output_path, exist_ok=True)
            json_output_path = os.path.join(subdir_output_path, subdir + ".json")

            command1 = f'{python_executable} "C:/Users/Public/Documents/MegaDetector_App/MegaDetector/megadetector/detection/run_detector_batch.py" "{model_path}" "{subdir_path}" "{json_output_path}" --output_relative_filenames --recursive --checkpoint_frequency 1000 --quiet'
            command2 = f'{python_executable} "C:/Users/Public/Documents/MegaDetector_App/MegaDetector/megadetector/postprocessing/postprocess_batch_results.py" "{json_output_path}" "{subdir_output_path}" --image_base_dir "{subdir_path}" --num_images_to_sample -1'

            # Add the class mapping argument only if it is provided
            if class_mapping_filename:
                command1 += f' --class_mapping_filename "{class_mapping_filename}"'

            commands = [command1, command2]

            for command in commands:
                run_command(command, env, log_file_path)
    open_file_explorer(output_directory)  # Open the directory after command completion

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

# Class Mapping File
class_mapping_frame = tk.Frame(pane)
pane.add(class_mapping_frame)
tk.Label(class_mapping_frame, text="Class Mapping File").pack()
entry_class_mapping = tk.Entry(class_mapping_frame, width=50)
entry_class_mapping.pack()
tk.Button(class_mapping_frame, text="Browse Mapping File", command=lambda: browse_path(entry_class_mapping, is_file=True)).pack()

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

# Shared Terminal Output
text_response = tk.Text(root, height=15)
text_response.pack(fill=tk.BOTH, expand=True)

root.mainloop()
