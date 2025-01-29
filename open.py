import os 
import requests
from bs4 import BeautifulSoup
import json 
from dotenv import load_dotenv
from typing import List
from IPython.display import Markdown, display, update_display
from openai import OpenAI
import time

OLLAMA_API = "http://localhost:11434/api/chat"
HEADER={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}
MODEL = "llama3.2"

