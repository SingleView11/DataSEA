import os,json, requests,sys,PyPDF2
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from get_pdfs import download_file
from utils import read_metadata, clean_llm_json_res
from longtext_api import LLM_long_api
from get_pdfs import download_pdfs_from_links, get_pdf_links_from_single_link

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
        return text
    
def analyze_ref_papers():
    links = []

    try:
        with open("draft/query_gs_res.json", 'r',  encoding='utf-8') as file:
            data = json.load(file)
        
        links = [entry.get('Source', '') for entry in data]
        print(links)
    except Exception as e:
        print(f"Error: {e}")

    

    pdf_links = []

    for link in links:
        res = get_pdf_links_from_single_link(link)
        for ele in res:
            print(ele)
            try:
                pdf_links.append( ele["links"])
                #  print(el)
            except Exception as e:
                continue
    # print(pdf_links)
    # return
    

    download_pdfs_from_links(pdf_links, 'draft/pdfs/refs')

    analyze_pdfs_with_dataset('draft/pdfs/refs', 'draft/ref_paper_evals_res.json')


def analyze_pdfs_with_dataset(folder_path, output_file):

    
    results = []  # Initialize an empty list to store the results
    
    # Iterate through all the files in the folder
    for filename in os.listdir(folder_path):
        try:
            file_path = os.path.join(folder_path, filename)
            
            text = ""

            # Check if the file is a PDF
            if filename.endswith('.pdf'):
                # Extract text using the pre-implemented function
                text = extract_text_from_pdf(file_path)
            # Check if the file is a TXT
            elif filename.endswith('.txt'):
                # Open and read the text file
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            else:
                # Skip files that are neither PDFs nor TXT
                continue
            
            # Analyze the text with dataset
            analyze_res = analyze_pdf_with_dataset(text)
            analyze_res["pdf local path"] = file_path
            analyze_res["pdf name"] = filename
            
            # Add the result to the results list
            results.append(analyze_res)
        except Exception as e:
            continue
    
    # Save the results into a JSON file
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)

def generate_instruction_prompt(dataset_name, dataset_info):
    instruction_prompt = f"""
You are provided with two inputs:

1. A dataset named '{dataset_name}', which is described as: 
   "{dataset_info}".

2. A string containing text from a research paper.

Your task is to:

- Determine if the research paper references the dataset '{dataset_name}' at any point.
- If the dataset is referenced, identify and extract the specific part of the paper where the dataset is mentioned.
- Additionally, provide detailed information about how the dataset is used in the paper. This might include, but is not limited to:
    - Whether the dataset is used for model training, analysis, validation, comparison, or any other purpose.
    - Any specific aspects of the dataset mentioned (e.g., size, features, or unique characteristics).
    - Any insights into the relevance of the dataset to the research being conducted.

Your output should be a JSON object with the following structure:

{{
  "dataset_referred": <true/false>,
  "reference_details": {{
    "dataset_name": "{dataset_name}",
    "dataset_usage": "<detailed description of how the dataset is used in the research paper>",
    "related_text": "<specific excerpt from the paper where the dataset is mentioned or discussed>"
    "application_field": "<application domains of the paper, in the form of a list of keywords and their descriptions, and into a josn dict >"
    ...: any other useful info you think, can be left as blank
  }}
}}

Instructions:
- If the dataset '{dataset_name}' is not mentioned in the paper, set "dataset_referred" to false.
- If the dataset is mentioned, set "dataset_referred" to true and provide detailed information in the "reference_details" field.
- Ensure that "related_text" contains an exact or closely matching excerpt from the paper that supports your conclusion.
- If the dataset is referred to but no explicit usage is stated, provide an empty string for "dataset_usage".
"""
    return instruction_prompt

def analyze_pdf_with_dataset(text):
    dataset_name, dataset_info = read_metadata()
    prompt = generate_instruction_prompt(dataset_name,dataset_info)
    res = LLM_long_api(prompt, text)
    res_cleaned = clean_llm_json_res(res)
    return res_cleaned

if __name__ == "__main__":
    # analyze_pdfs_with_dataset("draft/pdfs", "draft/original_pdf_analysis.json")
    analyze_ref_papers()
    print()
# pdf_path = "draft/pdfs\\1708.07747.pdf"  # Replace with your file path
# text = extract_text_from_pdf(pdf_path)
# print(len(text))