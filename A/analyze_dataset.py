# load elements and visualize them
from try_download_ideas import clean_code_block, run_all_python_files_in_folder
import os
# get potential paper website link from 1. dataset websites 2. search engine
import sys
import os, json

# Get the absolute path to the parent directory of the S and E folders
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the S folder to sys.path so Python can find the module inside it
sys.path.append(os.path.join(parent_dir, 'E'))
sys.path.append(parent_dir)

from E.get_pdfs import delete_all_contents_in_folder, delete_all_files_in_folder

from E.longtext_api import LLM_long_api
from utils import read_metadata, read_metadata_dataset_websites, fetch_html_from_link

import os, glob

def delete_py_files_in_folder(folder_path):
    # Recursively find all .py files in the folder and subfolders
    py_files = glob.glob(os.path.join(folder_path, '**', '*.py'), recursive=True)
    
    # Delete each .py file found
    for py_file in py_files:
        try:
            os.remove(py_file)
            print(f"Deleted: {py_file}")
        except Exception as e:
            print(f"Error deleting {py_file}: {e}")

def delete_log_json_files_in_folder(folder_path):
    # Recursively find all .py files in the folder and subfolders
    py_files = glob.glob(os.path.join(folder_path, '**', '*_log.json'), recursive=True)
    
    # Delete each .py file found
    for py_file in py_files:
        try:
            os.remove(py_file)
            print(f"Deleted: {py_file}")
        except Exception as e:
            print(f"Error deleting {py_file}: {e}")

def get_analyze_code_for_all():
    
    # Path to the parent folder containing subfolders
    parent_folder = 'draft/dataset'
    delete_py_files_in_folder(parent_folder)
    delete_log_json_files_in_folder(parent_folder)

    # Iterate over all the folders inside 'draft/dataset' (first level)
    for folder_name in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder_name)
        
        # Check if the current path is a folder
        if os.path.isdir(folder_path):
            print(f"Folder: {folder_name}")
            file_info_list = get_file_info_list(folder_path)
            generate_code_for_analyzing(files_info=file_info_list, path=folder_path)



def get_file_info_list(dataset_folder, n = 500):
    """
    Reads the first n characters from each file in the specified folder and 
    returns an array of dictionaries containing the filename and file content.

    Parameters:
    - dataset_folder (str): Path to the folder containing the files.
    - n (int): The number of characters to read from each file.

    Returns:
    - List[Dict]: A list of dictionaries, each containing 'filename' and 'content'.
    """
    
    # List to store the dictionaries for each file
    file_info_list = []

    try:
        # Iterate over all the files in the dataset folder
        for filename in os.listdir(dataset_folder):
            file_path = os.path.join(dataset_folder, filename)
            
            # Check if it's a file (not a folder)
            if os.path.isfile(file_path):
                try:
                    # Open the file and read the top n characters
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_content = file.read(n)
                    
                    # Create a dictionary with filename and file content
                    file_info = {
                        'filename': filename,
                        'content': file_content
                    }
                    
                    # Add the dictionary to the list
                    file_info_list.append(file_info)

                
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
    
    except Exception as e:
        print(f"Error accessing folder {dataset_folder}: {e}")

    return file_info_list



    # Return the array of dictionaries

def generate_code_for_analyzing(files_info, path, error_info):
    generate = True
    try:
        dataset_name, dataset_info = read_metadata()
        ppt = generate_instruction_prompt(files_info, path, error_info)
        res = LLM_long_api(ppt, files_info)
        print(res)
        res = clean_code_block(res)
    except Exception as e:
        res = ""
        generate = False
        print(f"Error {e}")

    file_path1 = f"{path}/analyze_dataset.py"
    print(file_path1)

    with open(file_path1, 'w') as file:
        file.write(res)

    status_info = {
        "res": res,
        "generate": generate
    }
    with open(f"{path}/status_log.json", 'w') as file:
        json.dump(status_info, file, indent=4 )

        
def generate_instruction_prompt(files_info, path, error_info = ""):

    dataset_name, dataset_info = read_metadata()

    """
    Generate an instruction prompt for an LLM to generate Python code to read 
    and visualize the elements of a dataset.

    Parameters:
    - variable (str): The variable name that will hold the dataset.
    - dataset_name (str): The name of the dataset.
    - dataset_info (list): A list of dictionaries containing file names and the 
                           head starting characters of the files (if applicable).

    Returns:
    - str: The generated instruction prompt.
    """
    # Construct the base prompt
    prompt = f"""
    # Instruction:
    Generate Python code to load the dataset '{dataset_name}', retrieve the first 10 samples, and visualize them.

    1. If the dataset '{dataset_name}' is famous (e.g., MNIST, CIFAR-10), use existing libraries to load it directly.
    2. If the dataset is not famous or there are no existing libraries, manually process the local dataset files provided below.
    3. Visualize the first 10 samples using matplotlib or another standard Python library.
    4. Ensure that all parts of the code (including file loading, sample extraction, and visualization) have proper try-except blocks to handle potential errors such as missing files, incorrect formats, or other exceptions. The except block should log or print an appropriate error message.

    ## Dataset Information:
    Below are some info about the dataset:
    {dataset_info}

    ## Local potential Dataset Files:
    Below are the potential local dataset files and their starting contents:
    {files_info}

    ### Task:
    - Write a Python program to load the dataset, extract the first 10 samples from the dataset and save it to a JSON file in the folder {path}.
    - Write a function to visualize these samples and save the plot figure in the same folder. Do not show them after plotting, just store them.
    - Add try-except blocks in all relevant parts of the code to catch and handle potential errors.
    - Write a function to generate a json file recording whether previous functions have worked successfully, if not working right then record error strings.

    ### Final Output:
    NOTE!!! You should only return me a Python file and do not include any other info, like text explanation or so. DO NOT WRITE EXPLANATION OUTSIDE OF PYTHON FILE YOU RETURN!!!

    ALSO DO NOT ADD QUOTATION MARKS at the beginning/ending of the code!

    Ensure the final output is runnable in the following structure:

    ```python
    import os
    import matplotlib.pyplot as plt

    # If the dataset is famous, load it directly
    # Otherwise if you cannot find code to load the dataset, like when the dataset is not famous, try to make use of local file info which may be dataset files.
    def load_dataset():
        try:
            ...
        except Exception as e:
            ...

    def get_first_10_samples():
        try:
            ...
        except Exception as e:
            ...

    def visualize_samples(samples):
        try:
            ...
        except Exception as e:
            ...
    
    def save_run_result():
        ...

    if __name__ == "__main__":
        try:
            # Load dataset, get the first 10 samples, and visualize them
            samples = get_first_10_samples()
            visualize_samples(samples)
        except Exception as e:
            ...

        try:
            save_run_result()
        except Exception as e:
            ...

    ```

    NOTE THAT YOU HAVE PREVIOUSLY GENERATED A VERSION OF CODE BUT IT COULD NOT RUN, the error log is: {error_info}, so try to avoid mistakes you have already made in the past.

    You should return plain Python code, and do not add any other info or wrap the whole Python code into a JSON file!
    """

    return prompt

def analyze_and_run_code():
    get_analyze_code_for_all()
    run_all_python_files_in_folder("draft/dataset")

import os, subprocess

# HYPERPARAMETER
self_repair_time = 3

def regenerate_idea(file_path, e):
    file_info = get_file_info_list(file_path)
    generate_code_for_analyzing(file_info, file_path, error_info = f"{e}")

def analyze_and_run_code_with_self_repair():
    get_analyze_code_for_all()
    folder_path = "draft/dataset"
    # Walk through all files and subfolders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the file is a Python file
            if file.endswith(".py"):
                try:
                    file_path = os.path.join(root, file)
                    print(f"Running: {file_path}")
                    len = 0

                    while len < self_repair_time:
                        try:
                            subprocess.run(["python", file_path], check=True)
                            print(f"Successfully ran: {file_path}")
                            break
                        except subprocess.CalledProcessError as e:
                            print(f"Error running {file_path}: {e} for time {len}")
                            regenerate_idea(file_path, e)
                            len += 1


                except Exception as e:
                    print(f"An unexpected error occurred while running {file_path}: {e}")
                # except Exception as e:
                #     print(f"Error running python file: {e}")



if __name__ == "__main__":
    

    print()