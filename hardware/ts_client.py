"""ThingSpeak REST client + helpers (standard library only, no pip install needed)."""
import json
import math
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_BASE = "https://api.thingspeak.com"

# Must match the ESP32 firmware (uploadMain)
FIELD_MAP = {1: "grain_temp", 2: "air_temp", 3: "humidity",
             4: "mq135", 5: "mq3", 6: "mq7", 7: "risk", 8: "gas_index"}


def fetch_feeds(channel_id, read_api_key="", results=1):
    params = {"results": results, "status": "true"}
    if read_api_key:
        params["api_key"] = read_api_key
    url = f"{API_BASE}/channels/{channel_id}/feeds.json?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code in (400, 401, 404):
            raise RuntimeError(f"Access denied / channel not found (HTTP {e.code}). "
                               "Check channel_id and read_api_key in config.py.") from None
        raise RuntimeError(f"HTTP {e.code} from ThingSpeak") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}") from None
    if body.strip() == "-1":
        raise RuntimeError("Access denied (ThingSpeak returned -1). Check channel_id and read_api_key.")
    return json.loads(body).get("feeds", [])


def dew_point(t, rh):
    """Magnus formula."""
    if t is None or rh is None or rh <= 0:
        return None
    a, b = 17.62, 243.12
    g = math.log(rh / 100.0) + a * t / (b + t)
    return round(b * g / (a - g), 2)


def normalize(feed):
    def num(key):
        try:
            v = feed.get(key)
            return None if v is None else float(v)
        except ValueError:
            return None

    row = {name: num(f"field{i}") for i, name in FIELD_MAP.items()}
    t = datetime.strptime(feed["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    status = feed.get("status") or ""
    parts = [p.strip() for p in status.split("|")]          # "LEVEL | AQ GOOD | FAN_ON | ..."
    row.update(
        entry_id=int(feed.get("entry_id") or 0), t=t, status=status,
        level=parts[0] if parts and parts[0] else "UNKNOWN",
        aq=parts[1].replace("AQ", "").strip() if len(parts) > 1 else "--",
        phase=parts[2] if len(parts) > 2 else "--",
    )
    row["dew_point"] = dew_point(row["air_temp"], row["humidity"])
    return row


def slope_per_hour(rows, key, window=1800):
    """Least-squares trend of `key` over the last `window` seconds, in units per hour."""
    if not rows:
        return None
    end = rows[-1]["t"]
    pts = [(r["t"], r[key]) for r in rows if r.get(key) is not None and end - r["t"] <= window]
    if len(pts) < 3:
        return None
    n = len(pts)
    mt, mv = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    den = sum((p[0] - mt) ** 2 for p in pts)
    if den == 0:
        return None
    return round(sum((p[0] - mt) * (p[1] - mv) for p in pts) / den * 3600, 2)