import json
import os,sys
# Get the absolute path to the parent directory of the S and E folders
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the S folder to sys.path so Python can find the module inside it
sys.path.append(os.path.join(parent_dir, 'S'))
sys.path.append(parent_dir)

# Now you can import the function from the S folder
from get_firstpage_links import get_links

from prompt_generation import fetch_html_from_link, clamp_prompt
from convert_json_format import convert_judge_info_in_file
from links_eval import save_array_to_json, LLMApi
from utils import read_dataset_name, read_metadata

def filter_json_data(json_file, callback=None):
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    filtered_data = []
    
    for element in data:
        try:
            # Directly accessing the properties without using .get()
            if element['judge_info']['is_dataset_paper_website'] == True:
                filtered_data.append(element)
            elif element['judge_info']['download_link_paper_exists'] == True:
                filtered_data.append(element)
            elif element['judge_info']['is_direct_paper'] == True:
                filtered_data.append(element)
        except (KeyError, TypeError) as e:
            # Skip the element if there's any issue accessing properties
            if callback:
                callback(f"Skipping element due to error: {e}")
            continue
    
    return filtered_data

def extract_links_and_paper_links():
    # Arrays to store the extracted links

    data = filter_json_data('draft/origin_paper_res_1.json')

    print(len(data))

    dataset_name = read_dataset_name()

    
    link_array = []
    paper_link_array = []
    
    for element in data:
        try:
            # Extract the "link" property
            link_array.append(element['link'])
            
            # Extract "download_link_paper" if it's not None
            if element['judge_info']['download_link_paper'] is not None:
                paper_link_array.append(element['judge_info']['download_link_paper'])
        
        except (KeyError, TypeError) as e:
            # Skipping in case of errors in accessing properties
            continue

    llm_raw_res = []

    for link in link_array:
        # print("adfafasfd")
        pdfls = get_potential_pdf_link(link, dataset_name)
        llm_raw_res.append(pdfls)
    
    try:
        # Save the array of strings into a JSON file
        with open('draft/pdf_prompt_res.json', 'w') as file:
            json.dump(llm_raw_res, file)
    except Exception as e:
        print(f"Error saving array to JSON: {e}")
 
    try:
        # Load the JSON data from the file
        with open('draft/pdf_prompt_res.json', 'r') as file:
            data = json.load(file)
        
        download_links_array = []
        
        # Iterate over each string in the array and convert it to JSON
        for item in data:
            try:
                if item.startswith('```json\n'):
                    item = item[len('```json\n'):].strip('` \n')
                # Convert the string to JSON format
                item_json = json.loads(item)
                
                # Extract all download links from the item
                for key in item_json:
                    download_link_info = item_json[key]
                    download_links_array.append({
                        "link": download_link_info["link"],
                        "format": download_link_info["format"]
                    })
            except json.JSONDecodeError as e:
                # Skip invalid JSON strings
                print(f"Error decoding JSON for item: {item} - {e}")
                continue

    except Exception  as e:
        print(f"Error decoding JSON from file: {e}")

    for paper_link in paper_link_array:
        download_links_array.append({
            "link": paper_link,
            "format": None
        })

    # for download_link in download_links_array:
    #     paper_link_array.append(download_link["link"])
    
    return download_links_array

def get_potential_pdf_link(link, dataset_name, desc = ""):
    

    html_content = fetch_html_from_link(link)

    prompt = f"""
    I have the HTML content of a website, and I need to find any direct download links for a specific academic paper. The paper is the original paper of dataset {dataset_name}. The website link is: "{link}". 

    The description of the paper is as follows:
    "{desc}".

    Based on this information, please search through the HTML content to find any direct download links for the paper in common formats like PDF, DOCX, TXT, etc. Return all such links and specify the format of each link.

    Remember you should give the direct link of paper but not other werid stuff like dataset!!

    Return the format in JSON with the following structure:
    {{
        downalod_link_1: {{
            "link": "https://aaa.com",
            "format": "pdf"
        }},
        downalod_link_2: {{
            "link": "https://bbb.com",
            "format": "txt"
        }},

        ...,

        downalod_link_n: {{
            "link": "https://nnn.com",
            "format": "other format"
        }},
    }}

    Note: just give the json, and do not add any extra words like adding the j-s-o-n letters and then give me the json!

    The website HTML:
    \"\"\"
    {html_content}
    \"\"\"
    """

    prompt = clamp_prompt(prompt)    

    res = LLMApi(prompt)

    return res

def save_download_links_to_json(download_links_array, file_path):
    try:
        # Save the array of download links into a JSON file
        with open(file_path, 'w') as file:
            json.dump(download_links_array, file, indent=4)
        print(f"Download links successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving download links to JSON: {e}")

def get_pdf_links_from_single_link(link):
    dataset_name, desc = read_metadata()
    res = get_potential_pdf_link(link, dataset_name, desc)
    download_links_array = []
    try:
        if res.startswith('```json\n'):
            res = res[len('```json\n'):].strip('` \n')
        # Convert the string to JSON format
        res_json = json.loads(res)
        
        # Extract all download links from the item
        for key in res_json:
            download_link_info = res_json[key]
            download_links_array.append({
                "links": download_link_info["link"],
                "format": download_link_info["format"]
            })
    except json.JSONDecodeError as e:
        # Skip invalid JSON strings
        print(f"Error decoding JSON for item: {res} - {e}")
    return download_links_array

import requests
from urllib.parse import urlparse
import uuid
def download_file(link, file_path):
    # Ensure the directory exists
    # os.makedirs('draft/pdfs', exist_ok=True)
    
    # Extract file name from the URL or generate one based on content type

    try:
        file_name = os.path.basename(urlparse(link).path)
    except Exception as e:
        file_name = uuid.uuid4()
    
    # Create a log dictionary to store the result
    log = {
        "link": link,
        "status": ""
    }
    
    # Make the request to download the file
    try:
        response = requests.get(link)
        response.raise_for_status()  # Check for HTTP errors
        
        # Determine the file extension from the Content-Type if it's missing in the URL
        content_type = response.headers.get('Content-Type')
        if not file_name:
            if 'pdf' in content_type:
                file_name = 'downloaded_file.pdf'
            elif 'text/plain' in content_type:
                file_name = 'downloaded_file.txt'
            elif 'text/csv' in content_type:
                file_name = 'downloaded_file.csv'
            else:
                log["status"] = "fail"
                log["error"] = f"Unsupported content type: {content_type}"
                return log

        # If the link doesn't end with a proper extension, append one based on the content type
        if not file_name.endswith(('.pdf', '.txt', '.csv')):
            if 'pdf' in content_type:
                file_name += '.pdf'
            elif 'text/plain' in content_type:
                file_name += '.txt'
            elif 'text/csv' in content_type:
                file_name += '.csv'
            else:
                log["status"] = "fail"
                log["error"] = f"Unsupported content type: {content_type}"
                return log
        
        # Set file path to save the file
        file_path = os.path.join(file_path, file_name)
        
        # Save the file in the correct format
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        log["status"] = "success"
        log["file_path"] = file_path
        print(f"File saved as {file_path}")
        
    except requests.exceptions.RequestException as e:
        log["status"] = "fail"
        log["error"] = str(e)
    
    # Record the result in a JSON file
    with open('draft/download_log.json', 'a') as log_file:
        log_file.write(json.dumps(log) + '\n')
    
    return log
# Example usage
# download_file('http://arxiv.org/pdf/1708.07747')

def download_pdfs_from_links(links, file_path):

    delete_all_files_in_folder(file_path)
    print(links)
    status_log = []

    # HYPERPARAMETER
    max_len = 5

    for link in links:
        max_len -= 1
        status = download_file(link, file_path)
        status_log.append(status)
        if(max_len < 0):
            break

    try:
        # Save the array of download links into a JSON file
        with open(f"{file_path}/download_log.json", 'w') as file:
            json.dump(status_log, file, indent=4)
        print(f"download_log saved")
    except Exception as e:
        print(f"Error saving download_log: {e}")

def download_all_pdfs():
    
    # Call the function to delete all files in the folder

    res = extract_links_and_paper_links()
    save_download_links_to_json(res, 'draft/pdf_links_res.json')

    links = [ele["link"] for ele in res]
    download_pdfs_from_links(links, "draft/pdfs")
    

def delete_all_files_in_folder(folder_path ):
    
    
    # Check if the folder exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"The folder '{folder_path}' was created.")
    
    try:
        # List all files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # Check if it is a file and delete it
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            else:
                print(f"Skipped: {file_path} is not a file.")
                
    except Exception as e:
        print(f"An error occurred while deleting files: {e}")

import shutil

def delete_all_contents_in_folder(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return

    try:
        # List all contents (files and subdirectories) in the folder
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            # If it's a file or symbolic link, delete it
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
                print(f"Deleted file: {item_path}")

            # If it's a directory, delete the directory and its contents
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Deleted folder and its contents: {item_path}")

    except Exception as e:
        print(f"An error occurred while deleting contents: {e}")


if __name__ == "__main__":
    # res = extract_links_and_paper_links()
    # save_download_links_to_json(res, 'draft/pdf_links_res.json')

    # get_pdf_links_from_single_link(dataset_name="mnist", link="https://ieeexplore.ieee.org/abstract/document/7966217")

    # res1 = download_file("http://arxiv.org/pdf/1708.07747")

    # print(res1)
    download_all_pdfs()
    print()




# def potential_paper_download_links_all_files():
#     # Define the path to the JSON file
#     json_file_path = 'draft/origin_paper_res_1.json'
    
#     # Initialize an empty list to store the selected links and download links
#     download_links = []
    
#     try:
#         # Read the JSON file
#         with open(json_file_path, 'r') as file:
#             data = json.load(file)
#     except FileNotFoundError:
#         print(f"Error: The file '{json_file_path}' was not found.")
#         return []
#     except json.JSONDecodeError:
#         print(f"Error: The file '{json_file_path}' contains invalid JSON.")
#         return []
    
#     # Process each element in the JSON array
#     for item in data:
#         try:
#             # Check if 'judge_info' is a dictionary and contains the binary properties
#             judge_info = item.get('judge_info')
            
#             if isinstance(judge_info, dict):
#                 is_dataset_paper_website = judge_info.get('is_dataset_paper_website', False)
#                 download_link_paper_exists = judge_info.get('download_link_paper_exists', False)
#                 is_direct_paper = judge_info.get('is_direct_paper', False)
                
#                 # If any of the binary properties is True, add the link and download_link (if exists) to the result array
#                 if is_dataset_paper_website or download_link_paper_exists or is_direct_paper:
#                     link_entry = {"link": item.get('link')}
#                     download_link = judge_info.get('download_link_paper')
#                     if download_link:
#                         link_entry["download_link"] = download_link
#                     download_links.append(link_entry)
#         except Exception as e:
#             print(f"Error processing item: {item}. Error: {e}")
    
#     return download_links