import requests

data = {
    "company_name": "Vellore Institute of Technology",
    "url": "https://vit.ac.in/"
}

response = requests.post("http://127.0.0.1:8000/generate_brochure/", json=data)
print(response.json())
