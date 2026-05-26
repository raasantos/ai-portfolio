import dataclasses
import json

import pandas as pd

from models import Job

EXCEL_PATH = "Funil_Vagas.sheets.xlsx"
JSON_PATH = "data/jobs.json"


def populate_jobs():
    df = pd.read_excel(EXCEL_PATH)

    df = df.rename(columns={
        "Empresa": "empresa",
        "Vaga": "vaga",
        "Link": "link",
        "Tipo": "tipo",
        "Status": "status",
        "Data aplicação": "data_aplicacao",
        "Próxima Ação": "proxima_acao",
        "Descrição": "descricao",
    })

    df = df.where(pd.notna(df), None)

    raw = df.to_dict(orient="records")

    jobs = [
        Job(id=f"job_{i + 1:03d}", **row)
        for i, row in enumerate(raw)
    ]

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([dataclasses.asdict(j) for j in jobs], f, ensure_ascii=False, indent=2)

    print(f"{len(jobs)} jobs written to {JSON_PATH}")


if __name__ == "__main__":
    populate_jobs()
