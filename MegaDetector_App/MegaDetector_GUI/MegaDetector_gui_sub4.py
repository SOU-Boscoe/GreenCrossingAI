import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter import scrolledtext
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

            command1 = f'{python_executable} "C:/Users/Public/Documents/MegaDetector_App/MegaDetector/megadetector/detection/run_detector_batch.py" "{model_path}" "{subdir_path}" "{json_output_path}"'

            if chk_recursive.get():
                command1 += ' --recursive'
            if chk_output_relative_filenames.get():
                command1 += ' --output_relative_filenames'
            if chk_include_max_conf.get():
                command1 += ' --include_max_conf'
            if chk_quiet.get():
                command1 += ' --quiet'
            if entry_image_size.get():
                command1 += f' --image_size {entry_image_size.get()}'
            if chk_use_image_queue.get():
                command1 += ' --use_image_queue'
            if entry_threshold.get():
                command1 += f' --threshold {entry_threshold.get()}'
            if entry_checkpoint_frequency.get():
                command1 += f' --checkpoint_frequency {entry_checkpoint_frequency.get()}'
            if entry_checkpoint_path.get():
                command1 += f' --checkpoint_path "{entry_checkpoint_path.get()}"'
            if entry_resume_from_checkpoint.get():
                command1 += f' --resume_from_checkpoint "{entry_resume_from_checkpoint.get()}"'
            if chk_allow_checkpoint_overwrite.get():
                command1 += ' --allow_checkpoint_overwrite'
            if entry_ncores.get():
                command1 += f' --ncores {entry_ncores.get()}'
            if class_mapping_filename:
                command1 += f' --class_mapping_filename "{class_mapping_filename}"'
            if chk_include_image_size.get():
                command1 += ' --include_image_size'
            if chk_include_image_timestamp.get():
                command1 += ' --include_image_timestamp'
            if chk_include_exif_data.get():
                command1 += ' --include_exif_data'
            if entry_overwrite_handling.get():
                command1 += f' --overwrite_handling {entry_overwrite_handling.get()}'

            command2 = f'{python_executable} "C:/Users/Public/Documents/MegaDetector_App/MegaDetector/megadetector/postprocessing/postprocess_batch_results.py" "{json_output_path}" "{subdir_output_path}" --image_base_dir "{subdir_path}" --num_images_to_sample -1'

            commands = [command1, command2]

            for command in commands:
                run_command(command, env, log_file_path)
    open_file_explorer(output_directory)  # Open the directory after command completion

def create_tooltip(widget, text):
    tooltip = ttk.Label(widget, text=text, background="yellow", relief=tk.SOLID, borderwidth=1)
    tooltip.pack_forget()
    def show_tooltip(event):
        tooltip.pack(side=tk.BOTTOM)
    def hide_tooltip(event):
        tooltip.pack_forget()
    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)

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

# Additional Options
options_frame = tk.Frame(pane)
pane.add(options_frame)

chk_recursive = tk.BooleanVar()
chk_output_relative_filenames = tk.BooleanVar()
chk_include_max_conf = tk.BooleanVar()
chk_quiet = tk.BooleanVar()
chk_use_image_queue = tk.BooleanVar()
chk_allow_checkpoint_overwrite = tk.BooleanVar()
chk_include_image_size = tk.BooleanVar()
chk_include_image_timestamp = tk.BooleanVar()
chk_include_exif_data = tk.BooleanVar()

chkbox_recursive = tk.Checkbutton(options_frame, text="Recursive", variable=chk_recursive)
chkbox_recursive.pack(anchor=tk.W)
create_tooltip(chkbox_recursive, "Recurse into directories, only meaningful if image_file points to a directory")

chkbox_output_relative_filenames = tk.Checkbutton(options_frame, text="Output Relative Filenames", variable=chk_output_relative_filenames)
chkbox_output_relative_filenames.pack(anchor=tk.W)
create_tooltip(chkbox_output_relative_filenames, "Output relative file names, only meaningful if image_file points to a directory")

chkbox_include_max_conf = tk.Checkbutton(options_frame, text="Include Max Conf", variable=chk_include_max_conf)
chkbox_include_max_conf.pack(anchor=tk.W)
create_tooltip(chkbox_include_max_conf, "Include the 'max_detection_conf' field in the output")

chkbox_quiet = tk.Checkbutton(options_frame, text="Quiet", variable=chk_quiet)
chkbox_quiet.pack(anchor=tk.W)
create_tooltip(chkbox_quiet, "Suppress per-image console output")

chkbox_use_image_queue = tk.Checkbutton(options_frame, text="Use Image Queue", variable=chk_use_image_queue)
chkbox_use_image_queue.pack(anchor=tk.W)
create_tooltip(chkbox_use_image_queue, "Pre-load images, may help keep your GPU busy; does not currently support checkpointing")

chkbox_allow_checkpoint_overwrite = tk.Checkbutton(options_frame, text="Allow Checkpoint Overwrite", variable=chk_allow_checkpoint_overwrite)
chkbox_allow_checkpoint_overwrite.pack(anchor=tk.W)
create_tooltip(chkbox_allow_checkpoint_overwrite, "Allow overwriting existing checkpoints")

chkbox_include_image_size = tk.Checkbutton(options_frame, text="Include Image Size", variable=chk_include_image_size)
chkbox_include_image_size.pack(anchor=tk.W)
create_tooltip(chkbox_include_image_size, "Include image dimensions in output file")

chkbox_include_image_timestamp = tk.Checkbutton(options_frame, text="Include Image Timestamp", variable=chk_include_image_timestamp)
chkbox_include_image_timestamp.pack(anchor=tk.W)
create_tooltip(chkbox_include_image_timestamp, "Include image datetime (if available) in output file")

chkbox_include_exif_data = tk.Checkbutton(options_frame, text="Include Exif Data", variable=chk_include_exif_data)
chkbox_include_exif_data.pack(anchor=tk.W)
create_tooltip(chkbox_include_exif_data, "Include available EXIF data in output file")

tk.Label(options_frame, text="Image Size").pack()
entry_image_size = tk.Entry(options_frame, width=20)
entry_image_size.pack()
create_tooltip(entry_image_size, "Force image resizing to a (square) integer size (not recommended to change this)")

tk.Label(options_frame, text="Threshold").pack()
entry_threshold = tk.Entry(options_frame, width=20)
entry_threshold.pack()
create_tooltip(entry_threshold, "Confidence threshold between 0 and 1.0, don't include boxes below this confidence in the output file")

tk.Label(options_frame, text="Checkpoint Frequency").pack()
entry_checkpoint_frequency = tk.Entry(options_frame, width=20)
entry_checkpoint_frequency.pack()
create_tooltip(entry_checkpoint_frequency, "Write results to a temporary file every N images; default is -1, which disables this feature")

tk.Label(options_frame, text="Checkpoint Path").pack()
entry_checkpoint_path = tk.Entry(options_frame, width=50)
entry_checkpoint_path.pack()
tk.Button(options_frame, text="Browse Checkpoint Path", command=lambda: browse_path(entry_checkpoint_path)).pack()
create_tooltip(entry_checkpoint_path, "File name to which checkpoints will be written if checkpoint_frequency is > 0, defaults to md_checkpoint_[date].json in the same folder as the output file")

tk.Label(options_frame, text="Resume from Checkpoint").pack()
entry_resume_from_checkpoint = tk.Entry(options_frame, width=50)
entry_resume_from_checkpoint.pack()
tk.Button(options_frame, text="Browse Resume Checkpoint", command=lambda: browse_path(entry_resume_from_checkpoint)).pack()
create_tooltip(entry_resume_from_checkpoint, "Path to a JSON checkpoint file to resume from, or 'auto' to find the most recent checkpoint in the same folder as the output file")

tk.Label(options_frame, text="Number of Cores").pack()
entry_ncores = tk.Entry(options_frame, width=20)
entry_ncores.pack()
create_tooltip(entry_ncores, "Number of cores to use; only applies to CPU-based inference")

tk.Label(options_frame, text="Overwrite Handling").pack()
entry_overwrite_handling = tk.Entry(options_frame, width=20)
entry_overwrite_handling.pack()
create_tooltip(entry_overwrite_handling, "What should we do if the output file exists? overwrite/skip/error (default overwrite)")

# Run Button
tk.Button(batch_frame, text="Run Batch", command=run_commands_thread).pack()

# Shared Terminal Output
text_response = scrolledtext.ScrolledText(root, height=15)
text_response.pack(fill=tk.BOTH, expand=True)

root.mainloop()
