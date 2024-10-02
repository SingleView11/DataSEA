import json, os, requests

def change_dataset_name(name):
    json_file_path = "draft/metadata.json"

    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Update the dataset_name
    data['dataset_name'] = name
    
    # Save the updated JSON back to the file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def read_dataset_name():
    with open("draft/metadata.json", 'r') as file:
        data2 = json.load(file)
    
    # Extract the "dataset_name" property
    dataset_name = data2['dataset_name']

    return dataset_name


def LLMApi(input_text, max_length=8888, model="gpt-4o-mini"):
    api_key = os.getenv('OPENAI_API_KEY')  # Get the API key from environment variables
    if not api_key:
        return "API key not found in environment variables."
    
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Clamp input text to max_length
    if len(input_text) > max_length:
        input_text = input_text[:max_length]  # Truncate the text if it's too long
    
    data = {
        "model": model,  # Ensure you're using a valid model, e.g., "gpt-4"
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

def fetch_html_from_link(link):
    """Fetches HTML content from a given link."""
    try:
        response = requests.get(link)
        response.raise_for_status()  # Raise an error for bad responses
            
        return response.text
    except requests.RequestException:
        return None  # Return None on error


from bs4 import BeautifulSoup
import requests

def fetch_html_from_link_no_script(link):
    """Fetches HTML content from a given link."""
    try:
        response = requests.get(link)
        response.raise_for_status()  # Raise an error for bad responses
        
        html_content = response.text
        
        # Try removing <script> tags from the HTML
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup.find_all('script'):
                script.decompose()  # Remove the <script> tags
            return str(soup)
        except Exception:
            return html_content  # In case of error, return the raw HTML content
    
    except requests.RequestException:
        return None  # Return None on error

def clamp_prompt(long_string, char_limit=8888):
    if len(long_string) > char_limit:
        return long_string[:char_limit] + '...'
    return long_string

def read_metadata(file_path='draft/metadata.json'):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Load the JSON data from the file
        metadata = json.load(file)
    
    # Extract dataset_name and convert the entire 'info' dictionary to a string
    dataset_name = metadata['dataset_name']
    dataset_info = json.dumps(metadata['info'])  # Convert the 'info' dictionary to a JSON-formatted string
    
    return dataset_name, dataset_info

def read_metadata_dataset_websites(file_path='draft/metadata.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Load the JSON data from the file
            metadata = json.load(file)
        
        # Extract dataset_name and convert the entire 'info' dictionary to a string
        dataset_websites = metadata["dataset_websites"]

        return dataset_websites
    except Exception as e:
        print(f"failed to read_metadata_dataset_websites, reason is : {e}")
        return []

# # Example usage:
# dataset_name, dataset_info = read_metadata()
# print(f"Dataset Name: {dataset_name}")
# print(f"Dataset Info: {dataset_info}")

def clean_llm_json_res(res):
    res_json = res
    try:
        if res.startswith('```json\n'):
            res = res[len('```json\n'):].strip('` \n')
        # Convert the string to JSON format
        res_json = json.loads(res)
    
    except Exception as e:
        # Skip invalid JSON strings
        print(f"Error decoding JSON for item: {res} - {e}")

    return res_json



def get_py_files_length(folder_path):
    total_length = 0
    # Traverse through all files in the folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):  # Only consider .py files
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    total_length += len(f.readlines())  # Add number of lines in the file
    return total_length

if __name__ == "__main__":
    folder_path = os.path.dirname(os.path.realpath(__file__))  # Get the current folder path
    total_lines = get_py_files_length(folder_path)
    print(f"The total number of lines in all .py files (including this script) is: {total_lines}")