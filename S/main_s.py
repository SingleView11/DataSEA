import sys, os
subfolder_path = os.path.join(os.getcwd(), 'S')
subfolder_path = os.path.join(os.getcwd(), 'E')
subfolder_path = os.path.join(os.getcwd(), 'A')
sys.path.append(subfolder_path)

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(parent_dir, 'E'))
sys.path.append(parent_dir)

import json
from links_eval import eval_pipeline
from E.get_pdfs import delete_all_contents_in_folder



# Function to process the "judge_info" field and convert it if valid JSON
def process_judge_info(data):
    for entry in data:
        # Check for the `json` code block prefix
        if entry['judge_info'].startswith('```json\n'):
            # Strip the prefix and any trailing backticks
            entry['judge_info'] = entry['judge_info'][len('```json\n'):].strip('` \n')

        try:
            # Attempt to convert judge_info to a JSON object
            entry['judge_info'] = json.loads(entry['judge_info'])
        except json.JSONDecodeError:
            # If not valid JSON, keep the original string
            pass
    return data

# Function to convert judge_info in a given input file and save to an output file
def convert_judge_info_in_file(input_file, output_file):
    # Read input data from a JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Process the judge_info field
    processed_data = process_judge_info(data)
    
    # Write the processed data to an output file
    with open(output_file, 'w') as f:
        json.dump(processed_data, f, indent=4)

    with open("draft/dataset_res.json", 'w') as f:
        json.dump(processed_data, f, indent=4)

import os
def create_folders(base_folder = 'draft'):

    delete_all_contents_in_folder("draft")
    # Define the folder structure
    subfolders = [
        os.path.join(base_folder, 'documents', 'htmls'),
        os.path.join(base_folder, 'documents', 'texts'),
        os.path.join(base_folder, 'pdfs', 'refs'),
        os.path.join(base_folder, 'pdfs_info')
    ]
    
    # Create the base folder if it doesn't exist
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    
    # Create subfolders
    for folder in subfolders:
        if not os.path.exists(folder):
            os.makedirs(folder)

        os.makedirs("draft", exist_ok=True)


    json_file_path = "draft/metadata.json"

    with open(json_file_path, 'w') as json_file:
        json.dump({
                "dataset_name": "",
                "info": {}
            }, json_file, indent=4)

def create_metadata_file(base_folder):
    # Define the path for metadata.json
    metadata_path = os.path.join(base_folder, 'metadata.json')
    
    # Metadata content with all fields left blank
    metadata_content = {
        "dataset_name": "",
        "info": {
            "description": "",
            "size": "",
            "scale": "",
            "author": "",
            "organization": "",
            "usage": "",
            "application_fields": [
                ""
            ],
            "keywords": [
                ""
            ]
        }
    }
    
    # Write metadata to the JSON file
    with open(metadata_path, 'w') as metadata_file:
        json.dump(metadata_content, metadata_file, indent=4)

def s_pipeline(dataset_name = "", dataset_desc = "", need_input = True):
    create_folders()
    eval_pipeline(dataset_name = dataset_name, dataset_desc = dataset_desc, need_input = need_input)
    convert_judge_info_in_file('draft/evals.json', 'draft/output.json')

if __name__ == "__main__":
    s_pipeline()

