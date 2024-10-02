import json

# Function to process the "judge_info" field and convert it if valid JSON
def process_judge_info(data):
    for entry in data:
        if entry['judge_info'].startswith('```json\n'):
            entry['judge_info'] = entry['judge_info'][len('```json\n'):].strip('` \n')
        
        try:
            entry['judge_info'] = json.loads(entry['judge_info'])
        except json.JSONDecodeError:
            pass
    return data

# Function to filter out entries with is_dataset_website true
def filter_dataset_websites(data):
    filtered_data = [
        entry for entry in data
        if isinstance(entry['judge_info'], dict) and entry['judge_info'].get('is_dataset_website') is True
    ]
    return filtered_data

# Function to read, process, and filter data
def filter_judge_info_in_file(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    processed_data = process_judge_info(data)
    filtered_data = filter_dataset_websites(processed_data)

    with open(output_file, 'w') as f:
        json.dump(filtered_data, f, indent=4)

# Example usage: load from evals.json and save filtered results to filtered_output.json
filter_judge_info_in_file('evals.json', 'filtered_output.json')
