from pathlib import Path
import json
from datetime import datetime, timezone

def utc_now(): return datetime.now(timezone.utc).isoformat()
def save_json(path, data):
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
def result(status="ok", **kwargs): return {"status":status,"timestamp":utc_now(),**kwargs}
