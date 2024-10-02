from get_paper import get_possible_papers
from get_pdfs import download_all_pdfs
from get_sorted_ref_papers import get_gs_papers
from get_dataset_metadata import whole_pipeline_get_metadata_and_txt_info
from analyze_ref_pdfs import analyze_ref_papers
from longtext_api import LLM_long_api

import os,json, requests,sys,PyPDF2
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from utils import clean_llm_json_res

import json

def get_final_metadata():
    metadata_file = 'draft/metadata.json'
    data_websites_file = 'draft/output.json'
    original_paper_file = 'draft/origin_paper_res_1.json'
    ref_ana_res_file = 'draft/ref_paper_evals_res.json'


    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    try:
    # Load output.json
        with open(data_websites_file, 'r', encoding='utf-8') as f:
            data_websites_file = json.load(f)

        # Add the dataset_websites property
        metadata['dataset_websites'] = data_websites_file
    except Exception as e:
        print(f"Error reading data webstes json(output.json), error is : {e}")

    try:
    # Load output.json
        with open(original_paper_file, 'r', encoding='utf-8') as f:
            original_papers = json.load(f)

        # Add the dataset_websites property
        metadata['original_papers'] = original_papers
    except Exception as e:
        print(f"Error reading original_papers json(origin_paper_res_1.json), error is : {e}")

    try:
    # Load output.json
        with open(ref_ana_res_file, 'r', encoding='utf-8') as f:
            ref_res_json = json.load(f)

        # Add the dataset_websites property
        metadata['reference papers'] = ref_res_json
    except Exception as e:
        print(f"Error reading refs json(ref_paper_evals_res.json), error is : {e}")


    # Save the updated metadata back to the same file (in place)
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4)

    print(f"Updated {metadata_file} with websites info.")

    return metadata

def prune_metadata():
    instruction = """
    You are tasked with pruning and refining a JSON file containing metadata for a dataset. The metadata properties include description, size, scale, author, organization, usage, application_fields, and keywords. These properties contain incomplete or vague information. In addition to this, the JSON file has fields such as dataset_websites, original_papers, and reference_papers that provide related evaluation and reference information.

    Your task is to:

    Examine the dataset_websites, original_papers, and reference_papers fields:

    The dataset_websites field contains links and associated evaluation information in the judge_info section. This includes descriptions, dataset size, authors, organization names, and relevant application fields.
    The original_papers field contains links to papers about the dataset, and some may provide metadata on the authors, descriptions, and usage.
    The reference_papers field includes references to the dataset, explaining how the dataset has been used in various research contexts.
    Prune and refine the following metadata fields:

    Description: Use the metadata in dataset_websites and original_papers to refine the dataset description. Ensure it is concise and informative, capturing the dataset's scope, purpose, and key features.
    Size: Extract any relevant size information from the evaluation data (e.g., the number of files, data points, or volume in gigabytes) to populate the size field.
    Scale: Refine the scale field using the metadata. Look for information on the scope of the dataset, such as the number of data points, sensors, or the geographical/temporal coverage.
    Author: Use metadata from original_papers and dataset_websites to identify the correct authors and populate the author field.
    Organization: Extract the relevant organizational information from the metadata, ensuring that the institutions involved in creating or supporting the dataset are accurately reflected.
    Usage: Populate the usage field with relevant information based on how the dataset has been used in research, as described in the reference_papers and dataset_websites metadata.
    Application Fields: Use the application fields from both dataset_websites and reference_papers to enhance the dataset’s application areas. Ensure the application fields describe how the dataset is used, such as in "mobile robotics," "autonomous driving," "object detection," etc.
    Keywords: Use descriptive keywords from the metadata to populate the keywords field. These should include terms relevant to the dataset's primary domain and use cases (e.g., "robotics," "autonomous driving," "data annotation").
    Ensure consistency and completeness:

    Review all metadata fields (description, size, scale, author, organization, usage, application_fields, and keywords) to ensure they are as detailed and accurate as possible.
    If information is still unavailable, leave the field blank or provide a reasonable placeholder based on general knowledge of similar datasets.
    Your final output should be a JSON file where the metadata fields are thoroughly pruned and refined, providing complete and accurate descriptions, authorship, and usage information based on the linked evaluation data.

    And you should return ONLY JSON with no expalnation or additional text!!

    """
    metadata_file = "draft/metadata.json"

    with open(metadata_file, 'r') as f:
        metadata_ori = json.load(f)
    metadata_str = json.dumps(metadata_ori, indent=4)
    res = LLM_long_api(instruction, metadata_str)
    res = clean_llm_json_res(res)

    with open("draft/metadata_pruned.json", 'w') as f:
        json.dump(res, f, indent=4)



    try:
        with open(metadata_file, 'r') as f:
            metadata_v1 = json.load(f)

        with open("draft/metadata_pruned.json", 'r') as f:
            metadata_pruned = json.load(f)
        metadata_v1["info"] = metadata_pruned["info"]

        with open("draft/metadata.json", 'w') as f:
            json.dump(metadata_v1, f, indent=4)
    except Exception as e:
        print(f"error combing pruned to original metadata: {e}")

def get_prune_metadata():
    get_final_metadata()
    prune_metadata()

def e_pipeline():
    get_possible_papers()
    download_all_pdfs()
    get_gs_papers()
    whole_pipeline_get_metadata_and_txt_info()
    analyze_ref_papers()
    get_prune_metadata()
    

if __name__ == "__main__":
    whole_pipeline_get_metadata_and_txt_info()
    analyze_ref_papers()
    get_prune_metadata()