import json


with open("data/jobs.json", "r") as f:
    jobs = json.load(f)


def search_jobs(tool_input: dict) -> str:
    query = tool_input["query"].lower()
    status_filter = tool_input.get("status", "").lower()

    results = []
    for j in jobs:
        matches_query = query in j["vaga"].lower() or query in j["empresa"].lower()
        matches_status = not status_filter or j.get("status", "").lower() == status_filter
        if matches_query and matches_status:
            results.append(j)

    return json.dumps(results, ensure_ascii=False)


def evaluate_fit(tool_input: dict) -> str:
    job_id = tool_input["job_id"]
    job = next((j for j in jobs if j["id"] == job_id), None)

    if not job:
        return json.dumps({"error": f"Job '{job_id}' not found"})

    return json.dumps({
        "empresa": job.get("empresa"),
        "vaga": job.get("vaga"),
        "descricao": job.get("descricao"),
        "requisitos": job.get("requisitos"),
        "skills": job.get("skills"),
    }, ensure_ascii=False)


def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "search_jobs":
        return search_jobs(tool_input)
    elif tool_name == "evaluate_fit":
        return evaluate_fit(tool_input)
    else:
        raise ValueError(f"Tool '{tool_name}' not recognized.")
