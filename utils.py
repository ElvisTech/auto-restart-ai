import json, logging, glob
logger = logging.getLogger(__name__)

def safe_parse_json(s):
    try:
        return json.loads(s)
    except Exception:
        return None

def find_json_files(glob_patterns):
    files = []
    for p in glob_patterns:
        import glob as _g
        files.extend(_g.glob(p))
    return files
