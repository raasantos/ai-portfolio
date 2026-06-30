from pydantic import BaseModel, Field
from typing import Optional

class JobRequest(BaseModel):
    text: str = Field(..., max_length=20000)

class JobResponse(BaseModel):
    empresa: str
    vaga: str
    remoto: bool
    salario_divulgado: bool
    salario: Optional[str] = None
    requisitos: list[str]
    beneficios: list[str]
    skills: list[str]
    palavras_ats: list[str]
    status_sugerido: str