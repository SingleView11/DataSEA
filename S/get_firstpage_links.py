import requests
from bs4 import BeautifulSoup

def search_google(query):
    # Make a request to Google Search
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        search_div = soup.find('div', {'id': 'search'})
        return str(search_div)
    else:
        return f"Error: {response.status_code}"

def save_to_file(content, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def extract_links(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    
    # Find all 'a' tags and get their href attributes
    for a_tag in soup.find_all('a', href=True):
        links.append(a_tag['href'])

    # with open("links.txt", 'w', encoding='utf-8') as link_file:
    #         for link in links:
    #             link_file.write(link + '\n')
                
    return links


def get_links(input_text):
    result = search_google(input_text)
    links = extract_links(result)
    return links

if __name__ == "__main__":
    # print(get_links("scope2 dataset"))
    
    query = input("Enter your search query: ")
    result = search_google(query)

    if "Error" not in result:
        save_to_file(result, "search_results.html")
        print("Search results saved to 'search_results.html'.")

        # Extract links and save to a separate file
        links = extract_links(result)
        with open("draft/links.txt", 'w', encoding='utf-8') as link_file:
            for link in links:
                link_file.write(link + '\n')
        
        print("Links saved to 'links.txt'.")
    else:
        print(result)
