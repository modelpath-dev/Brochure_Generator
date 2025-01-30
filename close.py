import os
import requests
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
from typing import List
from IPython.display import Markdown, display, update_display
from openai import OpenAI
import time

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if not (api_key and api_key.startswith('sk-proj-') and len(api_key) > 10):
    raise ValueError("Invalid or missing OpenAI API key")

MODEL = 'gpt-4o-mini'
openai = OpenAI()

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

class Website:
    def __init__(self, url):
        self.url = url
        self.title = "No title found"
        self.text = ""
        self.links = []
        
        try:
            response = requests.get(url, headers=header, timeout=10)
            response.raise_for_status()
            self.body = response.content
            soup = BeautifulSoup(self.body, 'html.parser')
            self.title = soup.title.string if soup.title else "No title found"
            
            if soup.body:
                for tag in soup.body(['script', 'style', 'img', 'input']):
                    tag.decompose()
                self.text = soup.body.get_text(separator='\n', strip=True)
                links = [link.get('href') for link in soup.find_all('a')]
                self.links = [link for link in links if link and link.startswith(('http', '/'))]
        except requests.exceptions.RequestException as e:
            print(f"Request error for {url}: {e}")
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

def get_links(url):
    try:
        website = Website(url)
        system_prompt = """
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
        user_prompt = f'Here is the list of links on the website of {website.url} - \n'
        user_prompt += "Please decide which of these are relevant web links for a brochure about the company:\n"
        user_prompt += "\n".join(website.links)

        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        return json.loads(result)
    except Exception as e:
        print(f"Error fetching relevant links: {e}")
        return {"links": []}

def get_details(url):
    try:
        result = "Landing page:\n"
        result += retry(url)
        links = get_links(url)
        print("Found links:", links)

        if "links" in links:
            for link in links["links"]:
                result += f"\n\n{link}\n"
                result += retry(link["url"])
        else:
            result += "\nNo relevant links found.\n"

        return result
    except Exception as e:
        print(f"Error getting details: {e}")
        return "Error retrieving details."

def brochure_user_prompt(company_name, url):
    try:
        user_prompt = f"You are looking at a company called: {company_name}\n"
        user_prompt += "Here are the contents of its landing page and other relevant pages. Use this information to build a brief brochure in markdown.\n"
        user_prompt += get_details(url)
        return user_prompt[:5000]
    except Exception as e:
        print(f"Error generating brochure prompt: {e}")
        return "Error generating user prompt."

def create_brochure(company_name, url):
    try:
        system_prompt = """
        You are an assistant that analyzes the contents of several relevant pages from a website and creates a short humorous brochure about the company for prospective customers, investors, and recruits.
        Respond in markdown and include details of company culture, customers, and careers/jobs if available.
        """
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": brochure_user_prompt(company_name, url)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error creating brochure: {e}")
        return "Error generating brochure."

def stream_brochure(company_name, url):
    try:
        system_prompt = """
        You are an assistant that analyzes the contents of several relevant pages from a website and creates a short humorous brochure about the company for prospective customers, investors, and recruits.
        Respond in markdown and include details of company culture, customers, and careers/jobs if available.
        """
        stream = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": brochure_user_prompt(company_name, url)}
            ],
            stream=True
        )
        
        response = ""
        display_handle = display(Markdown(""), display_id=True)
        for chunk in stream:
            response += chunk.choices[0].delta.content or ''
            response = response.replace("```", "").replace("markdown", "")
            update_display(Markdown(response), display_id=display_handle.display_id)
    except Exception as e:
        print(f"Error streaming brochure: {e}")
