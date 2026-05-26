def get_tools():
    return [
        {
            "name": "search_jobs",
            "description": "Busca vagas por título ou empresa. Use esta tool sempre que o usuário mencionar uma empresa ou cargo — inclusive quando pedir avaliação de fit, pois você precisará do job_id antes de chamar evaluate_fit.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query to find relevant job listings."},
                    "status": {"type": "string", "description": "Optional filter to specify the job status (e.g., 'applied', 'interview', 'offer')."}
                },
                "required": ["query"]
            },
        },
        {
            "name": "evaluate_fit",
            "description": "Avalia o fit entre o usuário e uma vaga específica. Requer um job_id válido — se não tiver, chame search_jobs primeiro para obtê-lo.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "The unique identifier of the job listing."},
                },
                "required": ["job_id"]
            },
        },
    ]