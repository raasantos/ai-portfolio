import requests
import json
import os
from dotenv import load_dotenv

BASE_URL = "https://api.anthropic.com/v1/messages"

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")


HEADERS = {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
}

def nivel_1_chamada_minima():
    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 256,
        "messages": [
            { 
                "role": "user",
                "content": "o que é um LLM? Responda em duas frases."
             }
        ]
    }

    response = requests.post(BASE_URL,headers=HEADERS, json=payload)
    data = response.json()

    print(data["content"][0]["text"])


def nivel_2_chamada_completa():
    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 512,
        "messages": [
            { 
                "role": "user",
                "content": "O que é RAG?"
             }
        ]
    }

    response = requests.post(BASE_URL,headers=HEADERS, json=payload)
    data = response.json()

    print("===Resposta Completa===")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def nivel_3_system_e_multiturn():
    # O system prompt define o comportamento do modelo
    # Ele é separado das messages — não entra no array de messages
    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 512,
        "system": "Você é um mentor técnico de IA. Responda de forma direta e objetiva, sem rodeios. Use exemplos práticos sempre que possível.",
        "messages": [
            # Turno 1 — usuário
            {"role": "user", "content": "O que é embedding?"},
            # Turno 2 — resposta anterior do assistente (você simula o histórico)
            {"role": "assistant", 
             "content": "Embedding é uma representação numérica de texto em um espaço vetorial. Palavras ou frases com significados similares ficam próximas nesse espaço. Por exemplo, 'rei' e 'rainha' terão vetores próximos entre si."},
            # Turno 3 — próxima pergunta do usuário
            {"role": "user", 
             "content": "E como isso é usado em RAG?"}
        ]
    }

    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    data = response.json()
 
    print("=== MULTI-TURN COM SYSTEM PROMPT ===")
    print(data["content"][0]["text"])



#nivel_2_chamada_completa()

#nivel_3_system_e_multiturn()

def nivel_4_streaming():
    payload = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 512,
        "stream": True,  # <-- ativa o streaming
        "messages": [
            {"role": "user", "content": "Explique function calling em LLMs em 3 parágrafos."}
        ]
    }
 
    # stream=True no requests para não baixar tudo de uma vez
    response = requests.post(BASE_URL, headers=HEADERS, json=payload, stream=True)
 
    print("=== STREAMING (token a token) ===")
 
    for line in response.iter_lines():
        if not line:
            continue
 
        line = line.decode("utf-8")
 
        # Cada linha começa com "data: "
        if not line.startswith("data: "):
            continue
 
        raw = line[len("data: "):]
 
        # Sinal de fim do stream
        if raw == "[DONE]":
            break
 
        event = json.loads(raw)
 
        # Só nos importa o delta de texto
        if event.get("type") == "content_block_delta":
            delta = event.get("delta", {})
            if delta.get("type") == "text_delta":
                print(delta["text"], end="", flush=True)
 
    print()  # quebra de linha no final


nivel_4_streaming()