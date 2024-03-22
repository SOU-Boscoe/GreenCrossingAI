import tkinter as tk
from tkinter import filedialog
import subprocess
import os

def browse_path(entry):
    folder_selected = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, folder_selected)

def run_command(command, env, log_file_path):
    with open(log_file_path, 'a') as log_file:  # Open the file in append mode
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, bufsize=1, universal_newlines=True)
        for line in process.stdout:
            log_file.write(line)  # Write the output to the log file
            text_response.insert(tk.END, line)
            text_response.see(tk.END)  # Scroll to the end
            root.update_idletasks()  # Update the GUI to reflect changes
        process.stdout.close()
        process.wait()

def run_commands_thread():
    base_image_folder = entry_image_folder.get()
    output_directory = os.path.join(entry_output_directory.get(), os.path.basename(base_image_folder) + "_results")
    os.makedirs(output_directory, exist_ok=True)

    log_file_path = os.path.join(output_directory, "command_output.log")  # Define the log file path

    python_executable = "python"  # Update this if necessary

    env = os.environ.copy()

    for subdir in os.listdir(base_image_folder):
        subdir_path = os.path.join(base_image_folder, subdir)
        if os.path.isdir(subdir_path):
            subdir_output_path = os.path.join(output_directory, subdir)
            os.makedirs(subdir_output_path, exist_ok=True)
            json_output_path = os.path.join(subdir_output_path, subdir + ".json")

            commands = [
                f'CUDA_VISIBLE_DEVICES=1 {python_executable} /shared/land_bridge/MegaDetector_App/MegaDetector/detection/run_detector_batch.py MDV5A "{subdir_path}" "{json_output_path}" --output_relative_filenames --recursive --checkpoint_frequency 1000 --quiet',
                f'CUDA_VISIBLE_DEVICES=1 {python_executable} /shared/land_bridge/MegaDetector_App/MegaDetector/api/batch_processing/postprocessing/postprocess_batch_results.py "{json_output_path}" "{subdir_output_path}" --image_base_dir "{subdir_path}" --num_images_to_sample -1'
            ]

            for command in commands:
                run_command(command, env, log_file_path)  # Run commands sequentially

def run_commands():
    run_commands_thread()  # Removed threading here to ensure GUI remains responsive

root = tk.Tk()
root.title("MegaDetector Runner")

tk.Label(root, text="Base Image Folder Path:").pack()
entry_image_folder = tk.Entry(root, width=50)
entry_image_folder.pack()
tk.Button(root, text="Browse", command=lambda: browse_path(entry_image_folder)).pack()

tk.Label(root, text="Root Output Directory (e.g., for 28Oct2022_results):").pack()
entry_output_directory = tk.Entry(root, width=50)
entry_output_directory.pack()
tk.Button(root, text="Browse", command=lambda: browse_path(entry_output_directory)).pack()

tk.Button(root, text="Run", command=run_commands).pack()

text_response = tk.Text(root, height=15)
text_response.pack()

root.mainloop()

