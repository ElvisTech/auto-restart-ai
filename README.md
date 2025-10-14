# Auto-Restart AI Agent (Modular) - Final Package

This project implements a modular auto-restart agent that:
- Tails text and JSON logs
- Uses a local Ollama model (phi3) via LangChain to analyze logs
- Produces MCP-style actions (restart systemd services, Docker containers, Kubernetes deployments)
- Validates actions against runbooks (RAG with FAISS) and protects against flapping
- Supports dry-run mode for safe testing

**Warning:** The executor runs real commands (systemctl, docker, kubectl). Keep `DRY_RUN=True` for testing.

## Layout
- `config.py` - configuration (log paths, model, dry-run, thresholds)
- `main.py` - orchestrator
- `tailer.py` - tails text and JSON logs
- `ai_agent.py` - LangChain/Ollama agent wrapper (model phi3)
- `mcp_actions.py` - handles MCP actions and calls executor
- `executor.py` - executes commands (service/container/pod restarts)
- `runbook_rag.py` - RAG index builder and query (sentence-transformers + faiss)
- `runbook.py` - runbook verifier (uses RAG if available)
- `memory_store.py` - flap protection
- `utils.py` - helpers
- `auto-restart-ai.service` - systemd unit configured for user `aiagent` and path `/opt/autorestart_ai`
- `requirements.txt` - python deps

## Quick install (recommended)
1. Copy project to `/opt/autorestart_ai`:
   ```bash
   sudo mkdir -p /opt/autorestart_ai
   sudo chown $(whoami):$(whoami) /opt/autorestart_ai
   unzip auto_restart_ai_final.zip -d /opt/autorestart_ai
   ```
2. Create a dedicated user (if not exists) and adjust ownership:
   ```bash
   sudo useradd --system --no-create-home --shell /usr/sbin/nologin aiagent
   sudo chown -R aiagent:aiagent /opt/autorestart_ai
   ```
3. Setup venv and install deps:
   ```bash
   cd /opt/autorestart_ai
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. (Optional) Build runbook index:
   ```bash
   source venv/bin/activate
   python -c "from runbook_rag import build_runbook_index; build_runbook_index()"
   ```
5. Copy systemd unit and enable:
   ```bash
   sudo cp auto-restart-ai.service /etc/systemd/system/auto-restart-ai.service
   sudo systemctl daemon-reload
   sudo systemctl enable auto-restart-ai.service
   sudo systemctl start auto-restart-ai.service
   ```
6. Monitor logs:
   ```bash
   sudo journalctl -u auto-restart-ai.service -f
   ```

## Notes
- Test thoroughly with `DRY_RUN=True`.
- Configure `config.py` to match your environment (log paths, model, Ollama URL).
- The RAG components require building the FAISS index locally.

