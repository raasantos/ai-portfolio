from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from models import JobRequest, JobResponse
from service import extract_job

router = APIRouter()

@router.post("/extract_job", response_model=JobResponse)
def extract_job_route(request: JobRequest):
    try:
        return extract_job(request.text)
    except ValueError as api_error:
        raise HTTPException(status_code=502, detail=f"Upstream API error: {api_error}")
    except RuntimeError as network_error:
        raise HTTPException(status_code=503, detail=f"Provider unavailable: {network_error}")
    except ValidationError as schema_error:
        raise HTTPException(status_code=422, detail=f"Schema mismatch: {schema_error}")
