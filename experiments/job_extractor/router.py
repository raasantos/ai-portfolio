from fastapi import APIRouter
from models import JobRequest, JobResponse
from service import extract_job

router = APIRouter()

@router.post("/extract_job", response_model=JobResponse)
def extract_job_route(request: JobRequest):
    return extract_job(request.text)