# Ollama + LangChain agent wrapper (model: phi3)
from langchain_ollama import Ollama
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from utils import logger
from config import OLLAMA_MODEL, OLLAMA_BASE_URL

class RawMCPTool(Tool):
    name = "raw_mcp_tool"
    description = "Accepts MCP JSON string and returns execution result."
    def _run(self, mcp_input: str) -> str:
        return mcp_input
    async def _arun(self, mcp_input: str) -> str:
        return self._run(mcp_input)

# initialize model
llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
memory = ConversationBufferMemory()
tools = [RawMCPTool()]
agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description", memory=memory, verbose=False)

def build_prompt(log_line):
    p = f"""You are an AI that inspects system and container logs and outputs a single JSON object (no extra text).
Choose one of the MCP actions: restart_service, restart_container, restart_pod, or action none.
Output must be valid JSON.

Log:
{log_line}

If you can extract a service/container/deployment name, output the appropriate action. Otherwise output {{"action": "none"}}.
"""
    return p

def analyze_log(log_line):
    prompt = build_prompt(log_line)
    resp = agent.run(prompt)
    logger.info(f"LLM returned: {resp}")
    return resp
