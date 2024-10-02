import os
import zipfile
import uuid
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

def zip_folder_with_uuid(folder_path = "draft", use_uuid = False):
    dataset_name, _ = read_metadata()
    
    # Generate a UUID
    unique_id = uuid.uuid4()
    
    # Ensure the destination folder 'experiment_results' exists
    results_folder = "experiment_results"
    os.makedirs(results_folder, exist_ok=True)
    zip_filename = os.path.join(results_folder, f"{dataset_name}.zip")
    if use_uuid:
        zip_filename = os.path.join(results_folder, f"{dataset_name}_{unique_id}.zip")
    
    # Zip the contents of the folder
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Write the file into the zip file
                zipf.write(file_path, os.path.relpath(file_path, folder_path))
    
    print(f"Folder '{folder_path}' has been zipped as '{zip_filename}' in the folder '{results_folder}'")

if __name__ == "__main__":
    zip_folder_with_uuid()