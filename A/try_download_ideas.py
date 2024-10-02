# get potential paper website link from 1. dataset websites 2. search engine
import sys
import os, json

# Get the absolute path to the parent directory of the S and E folders
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the S folder to sys.path so Python can find the module inside it
sys.path.append(os.path.join(parent_dir, 'E'))
sys.path.append(parent_dir)

from E.get_pdfs import delete_all_contents_in_folder

from E.longtext_api import LLM_long_api
from utils import read_metadata, read_metadata_dataset_websites, fetch_html_from_link

def try_ideas():
    os.makedirs("draft/ideas",exist_ok=True)
    os.makedirs("draft/dataset",exist_ok=True)

    delete_all_contents_in_folder("draft/ideas")
    delete_all_contents_in_folder("draft/dataset")

    with open("draft/download_ideas.json", 'r') as file:
        ideas = json.load(file)
    
    for idea in ideas:
        try:
            evaluate_idea(idea)

        except Exception as e:
            continue

def generate_instruction(uid, idea):

    dataset_name, dataset_info = read_metadata()

    prompt = f"""

    Write a python file to download the dataset {dataset_name}. Here are some other detail in case the dataset is not popular, so I provide some additional info.

    You are provided with an input dictionary stored in a variable called `input_data`. 
    It is the info about a dataset {dataset_name}, with info {dataset_info}. Your goal is to generate python code that can download the dataset.
    The structure of the dictionary is as follows:

    {idea}

    The real input is in the "input" section as this is an instruction prompt.

    NOTE THAT THE dictionary is ONLY FOR REFERENCE and it may contain FALSE INFO, so you can depend on it or not depend on it when writing code.

    Your task is to generate Python code for the following:

    - **Create a Python script file in the folder `draft/ideas/{uid}` with the name `get_dataset.py`, so its final path is `draft/ideas/{uid}/get_dataset.py`.** The folder draft/{uid}/ already exists.
    
    - **Define a function `download_dataset()` within this file.** 
        - This function should:
            - Download the dataset based on the dataset name and dataset info, and (if not enough), info provided in the input idea part, including potential alternative links.
            - Download the dataset based on the information provided in the `input_data` dictionary, including potential alternative links.
            - If you can already find infomation about the dataseat without using input json, you can write code to get it too.
            - Handle both direct downloads and cases where the download requires manual intervention following steps.
            - Add try-except blocks anywhere so that the code will function normally even if things go wrong.
            - Running the download_dataset will ensure that the dataset gets downloaded to the folder "draft/ideas/{uid}/downloads".
    
        - If after trying downloading directly or indirectly(like trying all potenial_links), not a single file is downloaded, you need to:
            - Print the required download steps as outlined in the `download_steps` section of the input.
            - Output these instructions clearly so that the user can follow them to manually download the dataset.
    - **Handle direct downloads:** 
        - If `direct_download` is set to "Yes", the function should use `requests` to download the file from `download_url` and save it in a folder called `draft/dataset/`. The filename should be derived from the URL or the dataset name, and it should match the specified `file_format` (e.g., `.csv`).
    
    - **Create directories if necessary:** 
        - Ensure that the folder `draft/dataset/{uid}` is created if it doesn't already exist.
    
    - **Error handling:** 
        - The function should check for errors during the download process, including connection errors, HTTP status codes, and file-writing issues. 
        - If the download fails, print a meaningful error message and proceed to try the next available download link (if any).
    
    - **Log useful information:**
        - After a successful download, print out useful metadata about the dataset from the `useful info` field, such as `homepage`, `description`, and links to related documentation or papers.

    - **File structure and naming:** 
        - Save the dataset with a filename based on the `dataset_name` and the appropriate `file_format`. For example, if the dataset is named `aaa` and the format is `xxx`, the file should be saved as `draft/dataset{uid}/aaa.xxx`.

    - **Generalization:** 
        - Ensure that the function is generalized to handle any properly formatted input dictionary of the same structure as provided in `input_data`, not just the specific example given.
    
    - **Edge cases and validation:**
        - Include validation for the existence of required fields like `download_url` and `file_format` in the `input_data`.
        - If a field is missing or invalid, the function should print an error and gracefully handle the situation without crashing.


    NOTE THAT the download link may be a link to files like csv/txt/zip/json/... , but when you just fetch it using normal get request, you may just get an html file. so you need to add logic to judge the returned info of html, like judging wiht content-type info and improve downlaoding effects.
            

    Example code structure to start:

    ```python
    import os
    import requests

    def download_dataset():
        ...
        ...

        ...
    

    if __name__ == "__main__":
        download_dataset()

    Note that the example code may be wrong, so do not really rely on it. You should generate code on your own.

    You should only return python code that is content of get_dataset.py, and do not add any extra info. DO NOT ADD A SINGLE LETTER OUTSIDE OF THE PYTHON CODE!

    And for the result python code, the function download_dataset, once run, will do all the job. You can add additional function to assist it, but this function must exist and can be run without calling parameters.

    """
    return prompt

import uuid

def clean_code_block(code_str):
    # Remove the surrounding ```python at the beginning and ``` at the end
    if code_str.startswith("```python"):
        code_str = code_str[len("```python"):].lstrip()  # Remove the leading ```python and any extra whitespace
    if code_str.startswith('"```python'):
        code_str = code_str[len('"```python'):].lstrip()  # Remove the leading ```python and any extra whitespace
    
    if code_str.endswith("```"):
        code_str = code_str[:-len("```")].rstrip()  # Remove the trailing ``` and any extra whitespace
    
    

    return code_str

def evaluate_idea(idea):


    try:
        uid = str(uuid.uuid4())
        instruction = generate_instruction(uid, idea)

        os.makedirs(f"draft/ideas/{uid}", exist_ok=True)

        
        res = LLM_long_api(instruction, json.dumps(idea))

        res = clean_code_block(res)

        file_path1 = f"draft/ideas/{uid}/get_dataset.py"
        file_path2 = f"draft/get_dataset.py"

        with open(file_path1, 'w') as file:
            file.write(res)

        with open(file_path2, 'w') as file:
            file.write(res)

        status_info = {
            "idea": idea,
            "res": res,
        }
        with open(f"draft/ideas/{uid}/status.json", 'w') as file:
            json.dump(status_info, file, indent=4 )
    except Exception as e:
        print(f"code generation for {idea} fail beacuse: {e}")

import os
import subprocess
def run_all_python_files_in_folder(folder_path):
    """
    Recursively find and run all Python files in a folder and its subfolders.
    """
    # Walk through all files and subfolders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the file is a Python file
            if file.endswith(".py"):
                try:
                    file_path = os.path.join(root, file)
                    print(f"Running: {file_path}")
                    
                    # Use subprocess to run the Python file
                    try:
                        subprocess.run(["python", file_path], check=True)
                        print(f"Successfully ran: {file_path}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error running {file_path}: {e}")
                    except Exception as e:
                        print(f"An unexpected error occurred while running {file_path}: {e}")
                except Exception as e:
                    print(f"Error running python file: {e}")

def try_ideas_and_run_code():
    try_ideas()
    run_all_python_files_in_folder("draft/ideas")

if __name__ == "__main__":
    try_ideas()
    run_all_python_files_in_folder("draft/ideas")










