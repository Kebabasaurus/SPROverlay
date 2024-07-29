import os

def create_settings_file(file_name):
    """Create the settings file with specified content."""
    # Define the content for the settings file
    settings_content = """DeltaWindow
Deltax = 50
Deltay = 30

DashWindow
Dashx = 740
Dashy = 830
-----------------------------------------------------^Windows^-----------------------------------------------------
"""

    # Get the current directory where the script is located
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, file_name)

    # Write the settings content to the file
    with open(file_path, 'w') as file:
        file.write(settings_content)
    
    print(f"Settings file created at {file_path}")

if __name__ == "__main__":
    # Define the name for the settings file
    settings_file_name = 'settings.txt'
    create_settings_file(settings_file_name)
