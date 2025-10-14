import json
from utils import safe_parse_json, logger
from executor import restart_service, restart_container, restart_pod
from runbook import verify_with_runbook
from memory_store import FlapProtector
from config import FLAP_THRESHOLD, FLAP_WINDOW_MIN

flap = FlapProtector(threshold=FLAP_THRESHOLD, window_min=FLAP_WINDOW_MIN)

def handle_mcp_text(mcp_text, raw_log=None):
    data = safe_parse_json(mcp_text)
    if not data:
        return {"ok": False, "reason": "no_json", "raw": mcp_text}
    action = data.get("action")
    params = data.get("parameters", {})
    if action == "none":
        return {"ok": True, "action": "none"}
    entity = params.get("service_name") or params.get("container_name") or params.get("deployment_name")
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
