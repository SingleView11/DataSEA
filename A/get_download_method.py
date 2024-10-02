# get potential paper website link from 1. dataset websites 2. search engine
import sys
import os, json

# Get the absolute path to the parent directory of the S and E folders
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the S folder to sys.path so Python can find the module inside it
sys.path.append(os.path.join(parent_dir, 'E'))
sys.path.append(parent_dir)

from longtext_api import LLM_long_api
from utils import read_metadata, read_metadata_dataset_websites, fetch_html_from_link

DOWNLOAD_IDEA_MAX_CHUNK = 10

def generate_llm_prompt(link):


    dataset_name, dataset_info = read_metadata()

    prompt = f"""
    You are tasked with analyzing the HTML content provided to identify how to download a dataset. The dataset information is as follows:

    - **Dataset Name**: {dataset_name}
    - **Dataset Info**: {dataset_info}

    ### Your Objective:
    1. **Download URL**: Extract the direct download link for the dataset file if it is explicitly provided in the HTML. If the link is hidden behind multiple steps (like clicking through to a secondary page), your task is to trace those steps and identify where the final download occurs. If no link is available, return 'None'.
    2. **File Format**: Determine the file format of the dataset (e.g., zip, tar, csv, json). If it is not explicitly mentioned, attempt to infer it from file extensions in the download URL or surrounding information.
    3. **Download Steps**: Provide clear, step-by-step instructions to acquire the dataset. This may include:
    - Clicking a direct download link.
    - Navigating to another webpage to continue the download process, if there is no direct link and a download page link is available.
    - Completing necessary forms or accepting terms to access the dataset.
    - Any other process required to reach the final dataset.

    You should try your best to find the direct download link of the dataset. Even if direct links do not exist, find possible indirect links.

    And sometimes there are direct download links but you misjudge them, so be more inclusive.

    NOTE!!! You should only return me a json file and do not contain any other info, like text explanation or so. DO NOT WRITE EXPLANATION OUTSIDE OF JSON FILE YOU RETURN!!!
    

    ### JSON Output Format:
    Present the output as a JSON object in the following structure:


    ```json
    {{
    "dataset_name": "{dataset_name}",
    "download_info": {{
        "download_url": "<Direct download URL or 'None' if not available>",
        "direct_download": "<If the download url is direct or none>",
        "useful info": "<any useful infos you find, like links to potential download pages even if they are not direct or certificated. this should be a dict>"
        "file_format": "<File format or 'Unknown'>",
        "potential_indirect_links": "<potential download links you think>"
        "download_steps": [
        {{
            "step": 1,
            "action": "<Description of the first step needed to download the dataset>"
        }},
        {{
            "step": 2,
            "action": "<Description of the second step, if applicable>"
        }},
        {{
            "step": 3,
            "action": "<Additional steps, if applicable>"
        }},
        ....,
        {{
            "step": n,
            "action": "<Additional steps, if applicable>"
        }},
        ]
    }}
    }}

    NOTE!!! You should only return me a json file and do not contain any other info, like text explanation or so. DO NOT WRITE EXPLANATION OUTSIDE OF JSON FILE YOU RETURN!!!

    """

    return prompt

def get_download_ideas():

    # only using 3 for test purpose
    # HYPERPARAMETER
    dataset_websites = read_metadata_dataset_websites()[:8]

    print(f"possible websites length is {len(dataset_websites)}")

    # print(dataset_websites)

    file_path = "draft/download_ideas.json"
    with open(file_path, 'w') as json_file:
        json_file.write('[')  # Start of the JSON array

    i = 0
    for ele in dataset_websites:
        try:

            link = ele["link"]
            print(f"starting analyzing download idea for link {link}...")

            ppt = generate_llm_prompt(link)
            html_content = fetch_html_from_link(link)
            dataset_download_idea = LLM_long_api(ppt, html_content, DOWNLOAD_IDEA_MAX_CHUNK)

            # dataset_download_idea_dict = json.loads(dataset_download_idea)

            with open(file_path, 'a', ) as json_file:
                if i > 0:  # Add a comma if it's not the first element
                    json_file.write(',')
                json.dump(dataset_download_idea, json_file, indent=4)
                print(f"Download idea for link {link} is generated")
                i += 1

        except Exception as e:
            print(f"download idea for {ele} is errored, error: {e}")


    with open(file_path, 'a') as json_file:
        json_file.write(']')  # End of the JSON array

if __name__ == "__main__":
    get_download_ideas()