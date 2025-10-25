import json
from utils import safe_parse_json, logger
from executor import restart_service, restart_container, restart_pod
from runbook import verify_with_runbook
from memory_store import FlapProtector
from config import FLAP_THRESHOLD, FLAP_WINDOW_MIN

flap = FlapProtector(threshold=FLAP_THRESHOLD, window_min=FLAP_WINDOW_MIN)

def _extract_json_str(mcp_text):
    try:
        if not isinstance(mcp_text, str):
            mcp_text = getattr(mcp_text, "content", str(mcp_text))
    except Exception:
        mcp_text = str(mcp_text)
    t = mcp_text.strip()
    # remove common code fences
    t = t.replace("```json", "").replace("```", "").strip()
    # extract the first JSON object if extra text exists
    start = t.find("{")
    end = t.rfind("}")
    if start != -1 and end != -1 and end > start:
        return t[start:end+1]
    return t

def handle_mcp_text(mcp_text, raw_log=None):
    sanitized = _extract_json_str(mcp_text)
    data = safe_parse_json(sanitized)
    if not data:
        return {"ok": False, "reason": "no_json", "raw": mcp_text}
    action = data.get("action")
    params = data.get("parameters", {}) or {}
    if action == "none":
        return {"ok": True, "action": "none"}
    entity = params.get("service_name") or params.get("container_name") or params.get("deployment_name")
    if not entity:
        return {"ok": False, "reason": "missing_entity", "action": action, "raw": data}
    if not verify_with_runbook(entity, raw_log):
        return {"ok": False, "reason": "runbook_disallow", "entity": entity}
    if not flap.should_restart(entity):
        return {"ok": False, "reason": "flap_threshold_not_met", "count": len(flap.store[entity])}
    if action == "restart_service":
        ok, out = restart_service(entity)
        if ok: flap.reset(entity)
        return {"ok": ok, "action": action, "entity": entity, "out": out}
    if action == "restart_container":
        ok, out = restart_container(entity)
        if ok: flap.reset(entity)
        return {"ok": ok, "action": action, "entity": entity, "out": out}
    if action == "restart_pod":
        ok, out = restart_pod(entity)
        if ok: flap.reset(entity)
        return {"ok": ok, "action": action, "entity": entity, "out": out}
    return {"ok": False, "reason": "unknown_action", "action": action}
