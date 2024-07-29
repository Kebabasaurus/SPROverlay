import subprocess
import os

# Directory where the scripts are located
script_directory = r'C:\Users\Tanks\OneDrive\Documents\Coding\iracingOverlay\Python\iracing projects'

def find_script(script_name):
    """Search for a script in the given directory."""
    for file in os.listdir(script_directory):
        if file.endswith('.py') and script_name in file:
            return os.path.join(script_directory, file)
    return None

# Define the scripts you want to run (exact names of the files)
scripts_to_run = ['Delta ChartV1.6.py', 'RPM GaugeV6.9.py']

# List of script paths to run
script_paths = []

for script_name in scripts_to_run:
    script_path = find_script(script_name)
    if script_path:
        script_paths.append(script_path)
    else:
        print(f"Script '{script_name}' not found in the directory.")

# Run all found scripts in parallel
processes = []
for script_path in script_paths:
    print(f"Running {script_path}...")
    process = subprocess.Popen(['python', script_path], shell=True)
    processes.append(process)

# Optionally, wait for all processes to complete
for process in processes:
    process.wait()

print("All scripts have been executed.")
