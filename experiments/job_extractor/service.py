from models import JobResponse
from anthropic_provider import extract_with_tool

def extract_job(text: str) -> JobResponse:
    fields = extract_with_tool(text)
    return JobResponse(**fields)