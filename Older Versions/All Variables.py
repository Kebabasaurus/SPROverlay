import irsdk
import time
import os
import pandas as pd

def read_variables_from_file(filename):
    """Reads variable names from a text file and returns a list of variable names."""
    if not os.path.isfile(filename):
        print(f"File {filename} does not exist.")
        return []
    
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    if not lines:
        print(f"The file {filename} is empty.")
        return []
    
    variables = [line.split()[0] for line in lines if line.strip()]
    return variables

def update_csv_file(file_path, data_dict):
    """Updates a CSV file with the latest data."""
    # Convert dictionary to DataFrame
    df = pd.DataFrame(list(data_dict.items()), columns=['Variable', 'Value'])
    
    if os.path.exists(file_path):
        # Append data to existing CSV file
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        # Create a new CSV file
        df.to_csv(file_path, index=False)

def main():
    # Path to the text file containing variable names
    variable_file = r'C:\Users\Tanks\OneDrive\Documents\Coding\iracingOverlay\Python\vars.txt'
    
    # Path to the CSV file where data will be saved
    csv_file = r'C:\Users\Tanks\OneDrive\Documents\Coding\iracingOverlay\Python\iracing_data.csv'

    # Read variables from the file
    variables = read_variables_from_file(variable_file)
    if not variables:
        print("No variables found in the file or file could not be read.")
        return

    # Initialize iRacing SDK
    ir = irsdk.IRSDK()

    # Check if iRacing is running
    if not ir.startup():
        print("iRacing not running. Make sure iRacing is started before running this script.")
        return

    print("Connected to iRacing. Fetching data points...")

    try:
        while True:
            # Freeze the buffer to get the latest data
            ir.freeze_var_buffer_latest()

            # Fetch values for each variable
            data_dict = {}
            for var_name in variables:
                try:
                    value = ir[var_name]
                    if value is not None:
                        data_dict[var_name] = value
                except KeyError:
                    data_dict[var_name] = 'Not found'

            # Print data types for debugging
            for var_name, value in data_dict.items():
                print(f"{var_name}: {value} (Type: {type(value)})")

            # Update the CSV file
            update_csv_file(csv_file, data_dict)

            print("Data updated in CSV file.")
            print("-" * 40)  # Separator for readability

            # Sleep for a bit to avoid flooding the CSV file
            time.sleep(1)

    except KeyboardInterrupt:
        print("Script terminated by user.")
    
    finally:
        ir.shutdown()
        


if __name__ == "__main__":
    main()
