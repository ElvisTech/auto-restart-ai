# Ollama + LangChain agent wrapper (model: phi3)
from langchain_ollama import ChatOllama
from utils import logger
from config import OLLAMA_MODEL, OLLAMA_BASE_URL

# initialize model
llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

def build_prompt(log_line):
    p = f"""You are an AI that inspects system and container logs and outputs a single JSON object.
Output ONLY raw JSON (no code fences, no markdown, no extra text).

Schema:
{{
  "action": "restart_service" | "restart_container" | "restart_pod" | "none",
  "parameters": {{
    "service_name" | "container_name" | "deployment_name": "<name>"
  }}
}}

Log:
{log_line}

Rules:
- If you can identify a service/container/deployment name, choose the appropriate action and include it under parameters.
- If you cannot identify the entity, output {{"action": "none"}}.
- Do not include any fields other than "action" and "parameters".
"""
    return p

def analyze_log(log_line):
    prompt = build_prompt(log_line)
    resp = llm.invoke(prompt)
    logger.info(f"LLM returned: {resp}")
    return resp
