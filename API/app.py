from fastapi import FastAPI
from pydantic import BaseModel
import open as open_module  
import close as close_module

app = FastAPI()

class BrochureRequest(BaseModel):
    company_name: str
    url: str
    module_type: str  

@app.post("/generate_brochure/")
def generate_brochure(request: BrochureRequest):
    if request.module_type == "open":
        brochure = open_module.create_brochure(request.company_name, request.url)
    elif request.module_type == "close":
        brochure = close_module.create_brochure(request.company_name, request.url)
    else:
        return {"error": "Invalid module_type. Choose 'open' or 'close'."}
    
    return {"brochure": brochure}