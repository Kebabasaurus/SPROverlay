import subprocess
import os

def find_executables(folder_path):
    """Find all .exe files in the given folder."""
    executables = []
    for file in os.listdir(folder_path):
        if file.endswith(".exe"):
            executables.append(os.path.join(folder_path, file))
    return executables

def launch_executable(path):
    """Launch an executable if it exists."""
    if path:
        try:
            subprocess.Popen(path, shell=True)
            print(f"Launched: {path}")
        except Exception as e:
            print(f"Failed to launch {path}: {e}")
    else:
        print("Executable not found.")

if __name__ == "__main__":
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Find all executables in the script directory
    executables = find_executables(script_dir)

    # Launch each executable
    for exe in executables:
        launch_executable(exe)
