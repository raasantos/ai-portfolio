from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Job:
    id: str
    empresa: Optional[str]
    vaga: Optional[str]
    link: Optional[str]
    tipo: Optional[str]
    status: Optional[str]
    data_aplicacao: Optional[str]
    proxima_acao: Optional[str]
    descricao: Optional[str]
    remoto: Optional[bool] = None
    salario_divulgado: bool = False
    salario: Optional[float] = None
    requisitos: list = field(default_factory=list)
    beneficios: list = field(default_factory=list)
    skills: list = field(default_factory=list)
    palavras_ats: list = field(default_factory=list)
