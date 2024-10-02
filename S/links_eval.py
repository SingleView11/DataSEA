from prompt_generation import prompts_links, clamp_prompt

import requests
import os

# get potential paper website link from 1. dataset websites 2. search engine
import sys
# Get the absolute path to the parent directory of the S and E folders
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from utils import change_dataset_name

def LLMApi(input_text):
    api_key = os.getenv('OPENAI_API_KEY')  # Get the API key from environment variables
    if not api_key:
        return "API key not found in environment variables."
    
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4o-mini", 
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input_text}
        ]
    }
    
    try:
        # Send POST request to OpenAI API
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        # If the response is successful (status code 200)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"An error occurred: {e}"

def test(dataset_name = "", desc = "", need_input = True):
    
    if need_input:
        dataset_name = input("Dataset name is: ")
        desc = input("Dataset description is: ")
    
    change_dataset_name(dataset_name)

    lipros = prompts_links(dataset_name=dataset_name, desc=desc)
    # print(lipros)
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

import json
def save_array_to_json(array, file_path="draft/evals.json"):
    """
    Saves an array to a JSON file.
    
    Parameters:
    array (list): The array to save.
    file_path (str): The path to the JSON file.
    """
    with open(file_path, 'w') as json_file:
        json.dump(array, json_file, indent=4)
    print(f"Array saved to {file_path}")

def eval_pipeline(dataset_name = "", dataset_desc = "", need_input = True):
    evals = test(dataset_name = dataset_name, desc = dataset_desc, need_input = need_input)
    save_array_to_json(evals)

if __name__ == "__main__":

    # t1 = LLMApi("oh shi bro")
    # print(t1)
    eval_pipeline()
    