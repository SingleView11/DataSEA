import json
from links_eval import eval_pipeline

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

    

# Example usage: load from evals.json and save to output.json


# convert_judge_info_in_file('evals.json', 'output.json')

if __name__ == "__main__":
    eval_pipeline()
    convert_judge_info_in_file('draft/evals.json', 'draft/output.json')

