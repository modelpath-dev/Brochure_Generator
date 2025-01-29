from fastapi import FastAPI
from pydantic import BaseModel
import open as open_module  
import close as close_module

app = FastAPI()

class BrochureRequest(BaseModel):
    company_name: str
    url: str

@app.post("/generate_brochure/")
def generate_brochure(request: BrochureRequest):
    brochure = close_module.create_brochure(request.company_name, request.url)
    return {"brochure": brochure}

