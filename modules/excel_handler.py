import pandas as pd
import os

def check_file_writable(file_path):
    """
    Checks if the Excel file can be opened for writing. Fails early if not.
    """
    try:
        # We try to open the file in append mode. This won't damage the file,
        # but it will fail with a PermissionError if the file is locked (e.g., open in Excel).
        with open(file_path, 'a'):
            pass
        return True
    except IOError:
        return False

def read_excel_file(file_path):
    """
    Reads the Excel file into a pandas DataFrame, ensuring all columns are text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: Excel tracker file not found at '{file_path}'")
    
    try:
        df = pd.read_excel(file_path, dtype=str)
        df = df.fillna('')
        print(f"Excel file '{file_path}' loaded successfully. Found {len(df)} rows.")
        return df
    except Exception as e:
        raise IOError(f"An error occurred while reading the Excel file: {e}")

def write_excel_file(df, file_path):
    """
    Saves the updated DataFrame back to the Excel file.
    """
    try:
        df.to_excel(file_path, index=False)
        print("[SUCCESS] File saved.")
    except PermissionError:
        raise PermissionError("FATAL ERROR: Could not save the file. Please close 'SeekingJobs.xlsx' and run the script again.")
    except Exception as e:
        raise IOError(f"An unexpected error occurred while saving the file: {e}")

