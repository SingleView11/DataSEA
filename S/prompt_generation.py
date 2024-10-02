import requests
from get_firstpage_links import get_links

def fetch_html_from_link(link):
    """Fetches HTML content from a given link."""
    try:
        response = requests.get(link)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.RequestException:
        return None  # Return None on error

def generate_prompt(link, dataset_name, desc = ""):
    """Fetches HTML and generates a prompt to analyze the dataset."""
    html_content = fetch_html_from_link(link)
    
    if html_content is None:
        return ""  # Return None if fetching failed

    # TODO: update and tune prompts

    prompt = f"""
    Determine whether the current website HTML is the website for the dataset ""{dataset_name}"". Here is some detail about the dataset: "{desc}"
    !!You should notice that the download link is for dataset and not article! If there is only download link of article and no dataset, it still should be judged as having no downlaod link!!
    If it is, give the dataset download link from the HTML content and provide some metadata about the website, such as description and basic info.

    If the download link is already the dataset, then note it. Otherwise, indicate that it is not. Do note that if the link is the dataset, then click it and a dataset will be downloaded, and it is not another website introducing or containing info about the dataset.

    If it is not, provide the reason.

    Return the format in JSON with the following structure:
    {{
        "is_dataset_website": <boolean>,
        "metadata": <object>,
        "download_link_dataset_exists": <boolean>,
        "download_link_dataset": <string>,
        "is_direct_data": <boolean>,
        "reason": <string>
    }}

    Note: just give the json, and do not add any extra words like adding the j-s-o-n letters and then give me the json!

    The website HTML:
    \"\"\"
    {html_content}
    \"\"\"
    """
    return prompt

def save_prompt_to_file(link, dataset_name, filename="gen_pro.txt"):
    """Fetches HTML, generates a prompt, and saves it to a file."""
    prompt = generate_prompt(link, dataset_name)
    print(link )
    print(dataset_name)

    #clamp
    prompt = clamp_prompt(prompt)
    
    if prompt is not None:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(prompt)

def clamp_prompt(long_string, char_limit=8000):
    if len(long_string) > char_limit:
        return long_string[:char_limit] + '...'
    return long_string

def prompts_links(dataset_name, desc = ""):
    links = get_links(dataset_name + " dataset")

    # HYPERPARAMETER
    # links = links[:10]

    res = []
    max_len = 5
    for link in links:
        max_len -= 1
        res.append({"link": link, "prompt": generate_prompt(link, dataset_name, desc)})
        print(link)
        if(max_len < 0):
            break
    return res

def test():
    dataset_name = input("Enter the dataset name: ")
    links = get_links(dataset_name)
    link = links[0]

    save_prompt_to_file(link, dataset_name=dataset_name)

def test2():
    dataset_name = input("Enter the dataset name: ")
    link = input("Enter the link name: ")

    save_prompt_to_file(link, dataset_name=dataset_name)


if __name__ == "__main__":
    test2()