import logging, time, threading
from tailer import tail_text_files, tail_json_files
from ai_agent import analyze_log
from mcp_actions import handle_mcp_text
from config import LOG_TEXT_FILES, LOG_JSON_GLOB, ERROR_KEYWORDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_text_line(line, source):
    if not any(k in line for k in ERROR_KEYWORDS):
        logger.info('not keywords')
        return
    logger.info(f"[ALERT] {source}: {line}")
    mcp_msg = analyze_log(line)
    mcp_text = getattr(mcp_msg, "content", str(mcp_msg))
    res = handle_mcp_text(mcp_text, raw_log=line)
    logger.info(f"Result: {res}")

def text_worker():
    for line, src in tail_text_files(LOG_TEXT_FILES):
        try:
            handle_text_line(line, src)
        except Exception as e:
            logger.exception("Error handling text line: %s", e)

def json_worker():
    for obj, src in tail_json_files(LOG_JSON_GLOB):
        try:
            summary = obj.get('message') or obj.get('msg') or str(obj)
            handle_text_line(summary, src)
        except Exception as e:
            logger.exception("Error handling json log: %s", e)

def main():
    t1 = threading.Thread(target=text_worker, daemon=True)
    t2 = threading.Thread(target=json_worker, daemon=True)
    t1.start()
    t2.start()
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
