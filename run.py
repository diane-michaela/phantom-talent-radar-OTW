import json
import time
import requests
from config import PB_API_KEY, PHANTOM_IDS

_BASE = "https://api.phantombuster.com/api/v2"
_HEADERS = {"X-Phantombuster-Key": PB_API_KEY}


def _launch(phantom_id: str):
    r = requests.post(f"{_BASE}/agents/launch", headers=_HEADERS, json={"id": phantom_id})
    r.raise_for_status()


def _poll(phantom_id: str, timeout: int = 1800, interval: int = 30) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(f"{_BASE}/agents/{phantom_id}", headers=_HEADERS)
        r.raise_for_status()
        data = r.json()
        status = data.get("status", "")
        if status == "finished":
            return data
        if status == "error":
            raise RuntimeError(
                f"Phantom {phantom_id} error: {data.get('errorMessage', 'unknown')}"
            )
        time.sleep(interval)
    raise TimeoutError(f"Phantom {phantom_id} did not finish within {timeout}s")


def _get_output(agent_data: dict) -> list:
    # PB v2: results live in resultObject on the agent record
    raw = agent_data.get("resultObject", "")
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str) and raw:
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, list) else [parsed]
        except json.JSONDecodeError:
            pass
    return []


def run_all() -> dict:
    results = {}
    for platform, phantom_id in PHANTOM_IDS.items():
        print(f"[run] {platform}: launching phantom {phantom_id}...")
        _launch(phantom_id)
        print(f"[run] {platform}: polling...")
        agent_data = _poll(phantom_id)
        output = _get_output(agent_data)
        results[platform] = output
        print(f"[run] {platform}: {len(output)} raw profiles")
    return results
