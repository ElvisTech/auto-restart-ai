import subprocess, shlex
from config import DRY_RUN
import logging
logger = logging.getLogger(__name__)

def _run_cmd(cmd):
    if DRY_RUN:
        logger.info(f"[DRY RUN] Would run: {cmd}")
        return True, "[DRY RUN]"
    try:
        if isinstance(cmd, list):
            res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            res = subprocess.run(shlex.split(cmd), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True, res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def restart_service(service_name):
    cmd = ["systemctl", "restart", service_name]
    ok, out = _run_cmd(cmd)
    return ok, out

def restart_container(container_name):
    cmd = ["docker", "restart", container_name]
    ok, out = _run_cmd(cmd)
    return ok, out

def restart_pod(deployment_name):
    cmd = ["kubectl", "rollout", "restart", "deployment", deployment_name]
    ok, out = _run_cmd(cmd)
    return ok, out
