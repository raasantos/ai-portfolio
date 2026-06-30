import os
import requests
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL_NAME = os.getenv("MODEL_NAME", "claude-haiku-4-5-20251001")

if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")

TOOL = {
    "name": "extract_job_fields",
    "description": "Extracts structured job information from unstructured text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "empresa": {"type": "string", "description": "Nome da empresa"},
            "vaga": {"type": "string", "description": "Título da vaga"},
            "remoto": {"type": "boolean", "description": "Indica se a vaga é remota"},
            "salario_divulgado": {"type": "boolean", "description": "Indica se o salário é divulgado"},
            "salario": {"type": "string", "description": "Faixa salarial, se divulgada"},
            "requisitos": {"type": "array", "items": {"type": "string"}, "description": "Lista de requisitos da vaga"},
            "beneficios": {"type": "array", "items": {"type": "string"}, "description": "Lista de benefícios oferecidos"},
            "skills": {"type": "array", "items": {"type": "string"}, "description": "Lista de habilidades necessárias para a vaga"},
            "palavras_ats": {"type": "array", "items": {"type": "string"}, "description": "Lista de palavras-chave para ATS (Applicant Tracking Systems)"},
            "status_sugerido": {"type": "string", "description": "Status sugerido para a vaga (e.g., 'aplicar', 'pesquisar mais', 'descartar')"}
        },
        "required": [
            "empresa", "vaga", "remoto", "salario_divulgado", "requisitos", "beneficios", "skills", "palavras_ats", "status_sugerido"]
    }
}

def extract_with_tool(text: str) -> dict:
    payload = {
        "model": MODEL_NAME,
        "max_tokens": 1024,
        "system": "Você é um extrator de dados de vagas de emprego. Extraia os campos estruturados da vaga fornecida.",
        "tools": [TOOL],
        "tool_choice": {"type": "tool", "name": "extract_job_fields"},
        "messages": [
            {"role": "user", "content": f"Extraia os campos da seguinte vaga:\n\n{text}"},
        ],
    }
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(ANTHROPIC_API_URL, json=payload, headers=headers, timeout=30)
    except requests.exceptions.RequestException as network_error:
        raise RuntimeError(f"Failed to reach Anthropic API: {network_error}") from network_error

    if not response.ok:
        raise ValueError(f"Anthropic API error {response.status_code}")

    data = response.json()

    tool_block = next(
        (block for block in data["content"] if block["type"] == "tool_use"),
        None
    )
    if tool_block is None:
        raise ValueError("API did not return a tool_use block. Response: " + str(data))

    return tool_block["input"]
