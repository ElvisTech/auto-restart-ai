# Runbook verifier. Uses RAG index if available, otherwise a conservative static mapping.
from pathlib import Path

STATIC = {
    "apache2": True,
    "payment-service": True,
    "web-frontend": True,
    "myapp": True
}

def verify_with_runbook(entity_name, log_line=None):
    try:
        from runbook_rag import query_runbook
        idx_dir = Path(__file__).parent / 'runbooks' / 'index'
        if idx_dir.exists():
            matches = query_runbook(entity_name, log_line or '', top_k=3)
            for m in matches:
                txt = (m.get('text') or '').lower()
                if entity_name.lower() in txt or 'restart' in txt:
                    return True
            return False
    except Exception:
        pass
    return STATIC.get(entity_name, False)
