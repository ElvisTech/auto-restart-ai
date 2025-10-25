# Config - adjust to your environment
LOG_TEXT_FILES = ["/var/log/mylog.log"]   # list of text log files to tail
LOG_JSON_GLOB = ["/var/log/app/*.json"]  # glob pattern for JSON structured logs (optional)
ERROR_KEYWORDS = ["error", "fail", "critical"]
FLAP_THRESHOLD = 2
FLAP_WINDOW_MIN = 5
DRY_RUN = True

OLLAMA_MODEL = "phi3"
OLLAMA_BASE_URL = "http://localhost:11434"

# Operational
SERVICE_USER = "aiagent"
INSTALL_PATH = "/opt/autorestart_ai"
