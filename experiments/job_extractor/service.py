from pydantic import ValidationError
from models import JobResponse
from anthropic_provider import extract_with_tool

def extract_job(text: str) -> JobResponse:
    fields = extract_with_tool(text)
    try:
        return JobResponse(**fields)
    except ValidationError as validation_error:
        raise ValueError(f"API returned fields that don't match the expected schema: {validation_error}") from validation_error
