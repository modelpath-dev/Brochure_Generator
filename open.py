import os
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
from typing import List
from IPython.display import Markdown, display
from openai import OpenAI
import time

OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}
MODEL = "llama3.2"

class Website:
    def __init__(self, url):
        self.url = url
        self.title = "No title found"
        self.text = ""
        self.links = []
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            self.body = response.content
            soup = BeautifulSoup(self.body, 'html.parser')
            self.title = soup.title.string if soup.title else "No title found"

            if soup.body:
                for tag in soup.body(['script', 'style', 'img', 'input']):
                    tag.decompose()
                self.text = soup.body.get_text(separator='\n', strip=True)
            
            links = [link.get('href') for link in soup.find_all('a')]
            self.links = [link for link in links if link]
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
        except Exception as e:
            print(f"Unexpected error processing {url}: {e}")
    
    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

def retry(url, retries=5, delay=2):
    for attempt in range(retries):
        try:
            return Website(url).get_contents()
        except Exception as e:
            print(f"Error occurred for {url}: {e}. Attempt {attempt + 1} of {retries}.")
            time.sleep(delay)
    print(f"Skipping {url} after {retries} failed attempts.")
    return f"Failed to retrieve contents for {url}\n"

SYSTEM_PROMPT = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company, 
such as links to an About page, or a Company page, or Careers/Jobs pages.
Respond in JSON:
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""

def get_links(url):
    try:
        website = Website(url)
        if not website.links:
            return {"links": []}
        
        user_prompt = f"Here is the list of links on the website of {website.url} - \n"
        user_prompt += "Please decide which of these are relevant web links for a brochure about the company:\n"
        user_prompt += "\n".join(website.links)
        
        ollama_client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
        response = ollama_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    except Exception as e:
        print(f"Error processing links for {url}: {e}")
        return {"links": []}

def get_details(url):
    try:
        result = "Landing page:\n"
        result += retry(url)
        links = get_links(url)
        
        print("Found links:", links)
        
        if "links" in links:
            for link in links["links"]:
                try:
                    result += f"\n\n{link}\n"
                    result += retry(link["url"])
                except Exception as e:
                    print(f"Error fetching link {link}: {e}")
        else:
            result += "\nNo relevant links found.\n"
        
        return result
    except Exception as e:
        print(f"Error processing details for {url}: {e}")
        return "Error retrieving details."

def brochure_user_prompt(company_name, url):
    try:
        user_prompt = f"You are looking at a company called: {company_name}\n"
        user_prompt += "Here are the contents of its landing page and other relevant pages. Use this information to build a brief brochure in markdown.\n"
        user_prompt += get_details(url)
        return user_prompt[:5000]
    except Exception as e:
        print(f"Error creating user prompt for {company_name}: {e}")
        return "Error generating user prompt."

def create_brochure(company_name, url):
    try:
        ollama_via_openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
        
        response = ollama_via_openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": brochure_user_prompt(company_name, url)}
            ],
        )
        
        result = response.choices[0].message.content
        display(Markdown(result)) 
        return result 
    except Exception as e:
        print(f"Error generating brochure for {company_name}: {e}")
        return "Error creating brochure."
