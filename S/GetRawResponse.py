import requests
import urllib.parse

def google_response(query):
    # Simulate a search in Google Chrome by crafting the Google search URL
    query = urllib.parse.quote_plus(query)
    search_url = f"https://www.google.com/search?q={query}"
    
    # User-agent is required to simulate a browser request, otherwise Google will block it
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Make the request to Google search
    response = requests.get(search_url, headers=headers)
    
    # Write the raw HTML response to a text file
    with open("raw_search_response.html", "w", encoding="utf-8") as file:
        file.write(response.text)


# Input a search term
query = input("Enter your search term: ")

# Perform the search
google_response(query)
