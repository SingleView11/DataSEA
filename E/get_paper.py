# get potential paper website link from 1. dataset websites 2. search engine
import sys
import os

# Get the absolute path to the parent directory of the S and E folders
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the S folder to sys.path so Python can find the module inside it
sys.path.append(os.path.join(parent_dir, 'S'))
sys.path.append(parent_dir)

# Now you can import the function from the S folder
from get_firstpage_links import get_links
from utils import read_dataset_name

from prompt_generation import fetch_html_from_link, clamp_prompt
from convert_json_format import convert_judge_info_in_file
from links_eval import save_array_to_json, LLMApi
from utils import change_dataset_name

def prompts_links(dataset_name, desc = ""):
    links = get_links("original paper of " + dataset_name + " dataset")
    res = []

    # HYPERPARAMETER
    max_len = 5
    for link in links:
        max_len -= 1
        res.append({"link": link, "prompt": generate_prompt_paper(link, dataset_name, desc)})
        print(link)
        if(max_len < 0):
            break
    return res

def generate_prompt_paper(link, dataset_name, desc = ""):
    """Fetches HTML and generates a prompt to analyze the dataset."""

    

    html_content = fetch_html_from_link(link)
    
    if html_content is None:
        return ""  # Return None if fetching failed

    # TODO: update and tune prompts

    prompt = f"""
    Determine whether the current website HTML is the website for the original paper of the dataset ""{dataset_name}"". Here is some detail about the dataset: "{desc}"
    
    Note that for \"the original paper of the dataset\", it means that the author of the paper creates the dataset, then writes a paper to introduce the details of the dataset {dataset_name}.
    It does not mean the author just use the dataset in his research, but means that the author creates the dataset.

    If it is, give the paper download link from the HTML content and provide some metadata about the website, such as description and basic info.

    If the download link is just the paper pdf(or possibly other format) then note it. Otherwise, indicate that it is not.

    If it is not the website of the orignal paper, provide the reason.

    Return the format in JSON with the following structure:
    {{
        "is_dataset_paper_website": <boolean>,
        "metadata": <object>,
        "download_link_paper_exists": <boolean>,
        "download_link_paper": <string>,
        "is_direct_paper": <boolean>,
        "reason": <string>
    }}

    Note: just give the json, and do not add any extra words like adding the j-s-o-n letters and then give me the json!

    The website HTML:
    \"\"\"
    {html_content}
    \"\"\"
    """
    return prompt

def get_json_evals():
    dataset_name = read_dataset_name()
    desc = ""
    # dataset_name = input("Dataset name is: ")
    # desc = input("Dataset description is: ")

    change_dataset_name(dataset_name)

    pps1 = prompts_links(dataset_name=dataset_name, desc=desc)
    print("pps1 fin")
    pps2 = dataset_link_prompts(dataset_name=dataset_name, desc=desc)
    # print(lipros)
    print("pps2 fin")
    # lipros = lipros[:2]
    lipros = merge_link_prompts(pps1, pps2)
    # print(lipros[0])
    # return
    ans = []

    for lipro in lipros:
        cur = {}
        cur["link"] = lipro["link"]
        print(cur["link"])
        ppt = clamp_prompt( lipro["prompt"])
        # print(ppt)
        cur["judge_info"] = LLMApi( ppt )
        ans.append(cur)

    return ans

def save_json_prompts():
    pps = get_json_evals()
    save_array_to_json(pps, file_path="draft/origin_paper_links_evals.json")

def dataset_link_prompts(dataset_name, desc = ""):
    links = getValidLinks("draft/dataset_res.json")
    res = []
    for link in links:
        res.append({"link": link["link"], "prompt": generate_prompt_paper(link, dataset_name, desc)})
        print(link)
    return res

import json

def getValidLinks(json_path):
    # Read the JSON file
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    # Filter elements where any of the 3 binary labels is True
    valid_links = []

    for element in data:
        try:
            if element['judge_info']['is_dataset_website']:
                valid_links.append(element)
            elif element['judge_info']['download_link_dataset_exists']:
                valid_links.append(element)
            elif element['judge_info']['is_direct_data']:
                valid_links.append(element)
        except Exception as e:
            continue
    return valid_links

def merge_link_prompts(lipros, dataset_link_prompts_array):
    # Initialize a dictionary to track links and counts
    link_dict = {}

    # Process lipros array and initialize "number" property
    for element in lipros:
        link = element['link']
        element['number'] = 1  # Initialize 'number' property
        link_dict[link] = element

    # Process dataset_link_prompts_array and merge
    for element in dataset_link_prompts_array:
        link = element['link']
        if link in link_dict:
            # If link already exists, increment the 'number' property
            link_dict[link]['number'] += 1
        else:
            # If link doesn't exist, add it with 'number' initialized to 1
            element['number'] = 1
            link_dict[link] = element

    # Convert the dictionary back into an array
    merged_array = list(link_dict.values())
    
    return merged_array


def get_possible_papers():
    # get_json_evals()
    save_json_prompts()
    convert_judge_info_in_file("draft/origin_paper_links_evals.json", "draft/origin_paper_res_1.json")




if __name__ == "__main__":
    # print('adf')
    # pro = generate_prompt_paper("https://example.com/", "example")
    # print(pro)

    get_possible_papers()