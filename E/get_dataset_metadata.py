import json, os, sys, requests, urllib
import csv
from bs4 import BeautifulSoup

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from utils import read_metadata, clean_llm_json_res
from longtext_api import LLM_long_api

# Function to extract links from the dataset
def extract_links_from_file(file_path = 'draft/output.json'):
    links = []
    
    # Read the JSON data from the file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Loop through each entry in the dataset
    for entry in data:
        # Extract the main 'link'
        if "link" in entry:
            links.append(entry["link"])
        
        # Extract the 'download_link_dataset' if it exists in the nested structure
        try:
            judge_info = entry.get("judge_info", {})
            if judge_info.get("download_link_dataset_exists", False):
                if "download_link_dataset" in judge_info:
                    links.append(judge_info["download_link_dataset"])
        except Exception as e:
            continue
        
    return links

def extract_all_links2(file_path = 'draft/origin_paper_res_1.json'):
    links = []
    
    # Read the JSON data from the file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Loop through each entry in the dataset
    for entry in data:
        # Extract the main 'link'
        if "link" in entry:
            links.append(entry["link"])
        
        # Extract links from 'judge_info'
        judge_info = entry.get("judge_info", {})
        if isinstance(judge_info, dict):
            # Extract 'download_link_paper' if it exists
            if judge_info.get("download_link_paper_exists", False):
                if "download_link_paper" in judge_info and judge_info["download_link_paper"]:
                    links.append(judge_info["download_link_paper"])
            
            # Extract 'url' from 'metadata' if it exists
            metadata = judge_info.get("metadata", {})
            if "url" in metadata:
                links.append(metadata["url"])

    return links


def download_files_dataset():

    all_links1 = extract_links_from_file()
    all_links2 = extract_all_links2()

    all_links = all_links1 + all_links2

    process_links(all_links)

def download_link_content(url):
    """
    Download the content from the given link if the size is less than 10MB.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP errors
        
        # Get content type and size from headers
        content_type = response.headers.get('Content-Type', '').lower()
        content_length = int(response.headers.get('Content-Length', 0))

        # Limit size to 10MB (10 * 1024 * 1024 bytes)
        if content_length > 10 * 1024 * 1024:
            print(f"File is too large ({content_length / (1024 * 1024):.2f} MB), skipping download.")
            return None

        # Check for valid content types (HTML, text, PDF)
        if 'text/html' in content_type or 'text/plain' in content_type or 'application/pdf' in content_type:
            content = response.content
            return content
        else:
            print(f"Unsupported content type: {content_type}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage:
# url = 'https://example.com/somefile.pdf'
# content = download_link_content(url)
# if content:
#     with open('downloaded_file', 'wb') as file:
#         file.write(content)

def download_link_content(url):
    """
    Download the content from the given link if the size is less than 10MB.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP errors

        # Get content type and size from headers
        content_type = response.headers.get('Content-Type', '').lower()
        content_length = int(response.headers.get('Content-Length', 0))

        # Limit size to 10MB (10 * 1024 * 1024 bytes)
        if content_length > 10 * 1024 * 1024:
            print(f"File is too large ({content_length / (1024 * 1024):.2f} MB), skipping download.")
            return None, None

        # Return content and its content type
        return response.content, content_type

    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None, None

def save_content_to_file(content, url, content_type, folder='draft/documents/htmls'):
    """
    Save the downloaded content to the specified folder, naming it based on the URL.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Parse the URL to get a simplified filename
    parsed_url = urllib.parse.urlparse(url)
    filename = parsed_url.netloc.replace('.', '_') + parsed_url.path.replace('/', '_')
    
    # Add extension based on content type
    if 'html' in content_type:
        filename += '.html'
    elif 'plain' in content_type:
        filename += '.txt'
    elif 'pdf' in content_type:
        filename += '.pdf'
    elif 'json' in content_type:
        filename += '.json'
    else:
        print(f"Unknown content type {content_type}, discarding file from {url}")
        return  # Discard the file

    file_path = os.path.join(folder, filename)


    try:
        # Write the content to the file
        with open(file_path, 'wb') as file:
            file.write(content)
        
        print(f"Saved content from {url} to {file_path}")
    except Exception as e:
        print()

def process_links(all_links):
    """
    Iterate over a list of links and download content for each.
    """
    for url in all_links:
        content, content_type = download_link_content(url)
        if content and content_type:
            save_content_to_file(content, url, content_type)

import PyPDF2  # or use pdfplumber if preferred

def extract_text_from_file(file_path):
    file_text = ""
    
    # Extract text based on the file type
    if file_path.endswith(".txt"):
        with open(file_path, 'r', encoding='utf-8') as f:
            file_text = f.read()

    elif file_path.endswith(".json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            file_text = json.dumps(json_data, indent=4)

    elif file_path.endswith(".csv"):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            file_text = "\n".join([", ".join(row) for row in reader])

    elif file_path.endswith(".html"):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                soup = BeautifulSoup(f, 'html.parser')

                # Extract links and important elements
                links = ""
                for a in soup.find_all('a', href=True):
                    links += f"Link text: {a.get_text()} - URL: {a['href']}\n"

                spans = ""
                for span in soup.find_all('span'):
                    spans += f"Span content: {span.get_text()}\n"
                
                # Extract images with their alt text
                images = ""
                for img in soup.find_all('img', src=True):
                    alt_text = img.get('alt', 'No alt text')
                    images += f"Image: {img['src']} - Alt text: {alt_text}\n"

                # Extract headings
                headings = ""
                for i in range(1, 7):  # Looping through h1 to h6
                    for heading in soup.find_all(f'h{i}'):
                        headings += f"Heading {i}: {heading.get_text()}\n"

                # Extract bold and italic text
                bold_text = ""
                for bold in soup.find_all(['b', 'strong']):
                    bold_text += f"Bold text: {bold.get_text()}\n"
                    
                italic_text = ""
                for italic in soup.find_all(['i', 'em']):
                    italic_text += f"Italic text: {italic.get_text()}\n"

                # Extract lists
                lists = ""
                for ul in soup.find_all('ul'):
                    for li in ul.find_all('li'):
                        lists += f"Unordered list item: {li.get_text()}\n"
                for ol in soup.find_all('ol'):
                    for li in ol.find_all('li'):
                        lists += f"Ordered list item: {li.get_text()}\n"

                # Extract tables
                tables = ""
                for table in soup.find_all('table'):
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        table_row = [cell.get_text() for cell in cells]
                        tables += " | ".join(table_row) + "\n"

                # Extract metadata
                meta_info = ""
                for meta in soup.find_all('meta'):
                    name = meta.get('name', 'No name')
                    content = meta.get('content', 'No content')
                    meta_info += f"Meta name: {name} - Content: {content}\n"

                # Get the remaining plain text
                text_content = soup.get_text()

                # Combine all extracted parts
                file_text = f"{text_content}\n\nImportant Links:\n{links}\n\nImportant Spans:\n{spans}\n\n"
                file_text += f"Images:\n{images}\n\nHeadings:\n{headings}\n\nBold Text:\n{bold_text}\n\n"
                file_text += f"Italic Text:\n{italic_text}\n\nLists:\n{lists}\n\nTables:\n{tables}\n\nMeta Info:\n{meta_info}"
            except Exception as e:
                print(f"html save error due to - {e}")

    elif file_path.endswith(".pdf"):
        # Using PyPDF2 to extract text from PDF
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            file_text = ""
            for page in reader.pages:
                file_text += page.extract_text()

        # Alternatively, if using pdfplumber:
        # with pdfplumber.open(file_path) as pdf:
        #     for page in pdf.pages:
        #         file_text += page.extract_text()

    return file_text

# Function to save the extracted text to a new .txt file
def save_text_to_file(file_text, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(file_text)

def remove_extra_blank_lines(text):
    # Split the text into lines, remove any empty lines, and join them back
    lines = text.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]  # Removes lines that are only whitespace
    return "\n".join(non_empty_lines)

# Main function to process all files in a folder
def process_folder(input_folder="draft/documents/htmls", output_folder= "draft/documents/texts"):
    os.makedirs(output_folder, exist_ok=True)
    
    # Iterate over all files in the input folder
    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Extract text from the file
        file_text = extract_text_from_file(file_path)
        
        # Remove extra blank lines
        file_text = remove_extra_blank_lines(file_text)
        
        # Save the extracted and cleaned text to a new .txt file in the output folder
        if file_text:
            output_file_name = os.path.splitext(file_name)[0] + ".txt"
            output_file_path = os.path.join(output_folder, output_file_name)
            save_text_to_file(file_text, output_file_path)
            print(f"Processed: {file_name} -> {output_file_name}")

def get_dataset_info_files_pipeline():
    download_files_dataset()
    process_folder()

def concatenate_txt_files(folder_path):
    full_text = ""
    
    # Loop through all files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        # Only process .txt files
        if file_path.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8') as file:
                full_text += file.read() + "\n\n"  # Add some spacing between each file
    
    return full_text

# Function to create the instruction prompt without the actual text
def generate_instruction_prompt():
    dataset_name, dataset_info = read_metadata()
    prompt =f"""
    You are provided with a detailed description from a folder of concatenated text files that may contain information about a dataset. 
    Your task is to extract the relevant dataset information and present it in the following JSON format:

    The basic info of dataset: its name is {dataset_name}, and its current info is {dataset_info}

    {{
        "dataset_name": "{dataset_name}",
        "info": {{
            "description": "<brief description of the dataset>",
            "size": "<size of the dataset (e.g., 1GB, 10,000 samples)>",
            "scale": "<scale of the memory of the dataset (e.g., 1tb, 1gb, 100mb, 10mb, 1mb, 100kb, ..., and not things like global or reginoal!!! it should be a number with a unit like mb or gb>",
            "author": "<author or creator of the dataset>",
            "organization": "<organization or institution responsible for the dataset>",
            "usage": "<how the dataset is typically used (e.g., model training, validation)>",
            "application_fields": [
                "<application_field (e.g., computer vision, NLP)>"
            ],
            "keywords": [
                "<keyword_1>",
                "<keyword_2>"
            ]
        }}
    }}

    Note that you should ONLY return a json file and no any other fukcing explanation info nonsense. JUST JSON!

    Use the information from the concatenated text to fill out the fields as accurately as possible. If any information is missing, leave the corresponding field empty or remove it.
    """
    return prompt

# Main function to run the entire process
def process_folder_and_generate_prompt(folder_path="draft/documents/texts"):
    # Step 1: Concatenate all text files into a single string (optional if just need instruction)
    concatenated_text = concatenate_txt_files(folder_path)

    concatenated_text = concatenated_text[:8888]
    
    # Step 2: Generate the instruction prompt
    instruction_prompt = generate_instruction_prompt()
    
    res = LLM_long_api(instruction_prompt, concatenated_text)
    res = clean_llm_json_res(res)
    # print(res)

    return res


def merge_jsons(generated_data, file_path='draft/metadata.json'):
    try:
        # Load the original JSON from the file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
    except FileNotFoundError:
        return f"Error: The file {file_path} was not found."
    except json.JSONDecodeError:
        return "Error: The JSON file could not be decoded."

    # Merge the 'info' section from generated_data into original_data
    try:
        def merge_datasets(original, generated):
            original['dataset_name'] = generated['dataset_name']

            for key, value in generated['info'].items():
                # if isinstance(value, list):
                #     # If it's a list, just add the new items to the old ones
                #     original['info'][key] = original['info'].get(key, []) + value
                # else:
                #     # For everything else, overwrite the original value
                original['info'][key] = value

            return original

        # Merge the two datasets
        merged_data = merge_datasets(original_data, generated_data)

        # Save the merged data back to the JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=4)

        # Return the merged data
        print(merged_data)

    except Exception as e:
        print( f"An error occurred during the merging process: {e}")

def whole_pipeline_get_metadata_and_txt_info():
    get_dataset_info_files_pipeline()
    res = process_folder_and_generate_prompt()
    merge_jsons(res)


if __name__ == "__main__":
    # process_folder_and_generate_prompt()
    res = process_folder_and_generate_prompt()
    merge_jsons(res)
    print()