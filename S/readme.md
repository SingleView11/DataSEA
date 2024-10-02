
# Search and Get Dataset 

## Usage Instructions
To run the main functionality of this project, execute the following command in the terminal:

```bash
python convert_json_format.py
```

This will trigger the main evaluation pipeline and the conversion of the `judge_info` field in the JSON files. You need to input a dataset name and a dataset description(optional) in cli.

The result is in output.json.

## Program Descriptions

### convert_json_format.py
This script processes the `judge_info` field in a JSON file, attempting to convert it into a valid JSON object. It reads data from an input file, processes the `judge_info` field, and saves the updated data to an output file. It also integrates with the `eval_pipeline` function from the `links_eval.py` script to execute the evaluation pipeline.

### convert_json_format2.py
Similar to the `convert_json_format.py` script, this script processes and converts the `judge_info` field in a JSON file. Additionally, it filters out entries where `is_dataset_website` is `True` and saves the filtered results to an output file.

### get_firstpage_links.py
This script performs a Google search for a given query, retrieves the search result page, extracts all the links, and saves them to a text file. It also has the capability to save the HTML content of the search results.

### GetRawResponse.py
This script simulates a Google search using a custom user-agent header, retrieves the raw HTML response from the search results, and saves it to a file. This raw HTML data can be used for further processing and extraction of links or information.

### links_eval.py
This script contains the `eval_pipeline` function that uses a language model to evaluate and classify links based on generated prompts. It sends user inputs through a predefined prompt and processes the model’s response. It saves the evaluated data in a JSON file for further analysis.

### prompt_generation.py
This script generates prompts for evaluating whether a given link is a dataset website. It retrieves HTML content from a link, creates a customized prompt with specific criteria, and checks if the website contains a dataset download link. The generated prompts are saved to a file and can be used for automated link evaluation.
