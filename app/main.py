# Capstone DevOps Project — Cloud-Native Delivery Engine
# Final-year B.Tech Capstone | Shwetank Pandey
# Focus: Progressive delivery + observability for a lightweight incident & change tracker

import os
import time
import socket
import sqlite3
import logging
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# ── Structured JSON logger (human-readable in local, machine-friendly in prod) ──
class CompactJsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "lvl": record.levelname,
            "msg": record.getMessage(),
            "src": record.name,
            "host": socket.gethostname(),
        }
        if record.exc_info:
            payload["err"] = self.formatException(record.exc_info)
        return json.dumps(payload)

log = logging.getLogger("capstone-devops")
handler = logging.StreamHandler()
handler.setFormatter(CompactJsonFormatter())
log.addHandler(handler)
log.setLevel(logging.INFO)

app = Flask(__name__)

# ── Config from env (overridable via ConfigMap / Secret) ──
APP_VERSION = os.getenv("APP_VERSION", "1.4.2")
APP_ENV = os.getenv("APP_ENV", "prod")
HOSTNAME = socket.gethostname()
DB_PATH = os.getenv("DATABASE_PATH", "incidents.db")
SERVICE_NAME = os.getenv("SERVICE_NAME", "capstone-devops-api")

# ── Prometheus metrics ──
REQ_COUNT = Counter(
    "capstone-devops_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)
REQ_LATENCY = Histogram(
    "capstone-devops_http_request_duration_seconds",
    "Request latency",
    ["path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)
ACTIVE_INCIDENTS = Gauge(
    "capstone-devops_active_incidents",
    "Number of currently open incidents"
)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'medium',
            status TEXT NOT NULL DEFAULT 'open',
            owner TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.before_request
def _timer():
    request._t0 = time.time()

@app.after_request
def _metrics(resp):
    if hasattr(request, "_t0"):
        REQ_LATENCY.labels(path=request.path).observe(time.time() - request._t0)
    REQ_COUNT.labels(
        method=request.method,
        path=request.path,
        status=resp.status_code
    ).inc()
    return resp

# ── Dashboard template (dark, slightly different aesthetic) ──
DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Capstone DevOps Project • Delivery Console</title>
<style>
  :root {
    --bg: #0b0e14;
    --card: #141922;
    --border: #1f2937;
    --accent: #f59e0b;
    --green: #10b981;
    --red: #ef4444;
    --text: #e5e7eb;
    --muted: #9ca3af;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: "Inter", system-ui, sans-serif; padding: 1.75rem; }
  .wrap { max-width: 980px; margin: 0 auto; }
  header { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 1.5rem; }
  .brand { font-size: 1.45rem; font-weight: 650; letter-spacing: -0.02em; color: var(--accent); }
  .meta { font-size: 0.8rem; color: var(--muted); margin-top: 0.2rem; }
  .pills { display: flex; gap: 0.4rem; }
  .pill { background: #1f2937; padding: 0.3rem 0.65rem; border-radius: 999px; font-size: 0.75rem; font-weight: 500; }
  .pill.ok { background: #064e3b; color: #6ee7b7; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; margin-bottom: 1.5rem; }
  .stat { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; }
  .stat label { display: block; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); margin-bottom: 0.3rem; }
  .stat value { font-size: 1.15rem; font-weight: 600; }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.9rem; }
  form { display: flex; gap: 0.5rem; margin: 0.75rem 0 1rem; }
  input, select { background: #0b0e14; border: 1px solid var(--border); color: var(--text); padding: 0.55rem 0.75rem; border-radius: 6px; flex: 1; }
  button { background: var(--accent); color: #111; border: 0; padding: 0.55rem 1rem; border-radius: 6px; font-weight: 600; cursor: pointer; }
  table { width: 100%; border-collapse: collapse; background: var(--card); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
  th, td { text-align: left; padding: 0.7rem 1rem; border-bottom: 1px solid var(--border); font-size: 0.9rem; }
  th { background: #0f141c; color: var(--muted); font-weight: 500; font-size: 0.75rem; text-transform: uppercase; }
  .sev-high { color: var(--red); font-weight: 600; }
  .sev-med { color: var(--accent); }
  .sev-low { color: var(--green); }
  footer { margin-top: 1.5rem; font-size: 0.75rem; color: var(--muted); display: flex; justify-content: space-between; }
  a { color: var(--accent); text-decoration: none; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <div class="brand">Capstone DevOps Project</div>
      <div class="meta">Incident & change tracker • progressive delivery console</div>
    </div>
    <div class="pills">
      <span class="pill ok">{{ env }}</span>
      <span class="pill">{{ version }}</span>
    </div>
  </header>

  <div class="stats">
    <div class="stat"><label>Runtime host</label><value class="mono">{{ hostname }}</value></div>
    <div class="stat"><label>Probe status</label><value style="color:#10b981">Healthy</value></div>
    <div class="stat"><label>Open incidents</label><value>{{ open_count }}</value></div>
    <div class="stat"><label>Metrics</label><value><a href="/metrics" target="_blank">Prometheus →</a></value></div>
  </div>

  <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1rem;margin-bottom:1.25rem;">
    <div style="font-weight:600;margin-bottom:0.4rem;">New incident / change</div>
    <form action="/api/v1/incidents" method="POST">
      <input name="title" placeholder="e.g. Canary rollout of payment service" required>
      <select name="severity">
        <option value="low">Low</option>
        <option value="medium" selected>Medium</option>
        <option value="high">High</option>
      </select>
      <button type="submit">Create</button>
    </form>
  </div>

  <table>
    <thead>
      <tr><th>ID</th><th>Title</th><th>Severity</th><th>Status</th><th>Created</th></tr>
    </thead>
    <tbody>
      {% for i in incidents %}
      <tr>
        <td class="mono">#{{ i[0] }}</td>
        <td>{{ i[1] }}</td>
        <td class="sev-{{ i[2] }}">{{ i[2]|upper }}</td>
        <td>{{ i[3] }}</td>
        <td class="mono" style="color:var(--muted)">{{ i[4] }}</td>
      </tr>
      {% else %}
      <tr><td colspan="5" style="text-align:center;color:var(--muted);padding:1.5rem;">No incidents yet. Create one above.</td></tr>
      {% endfor %}
    </tbody>
  </table>

  <footer>
    <span>Probes: <a href="/health/live">live</a> · <a href="/health/ready">ready</a> · <a href="/metrics">metrics</a></span>
    <span>Shwetank Pandey · Capstone 2026</span>
  </footer>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, severity, status, created_at FROM incidents ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    c.execute("SELECT COUNT(*) FROM incidents WHERE status = 'open'")
    open_count = c.fetchone()[0]
    conn.close()
    ACTIVE_INCIDENTS.set(open_count)
    return render_template_string(
        DASHBOARD,
        version=APP_VERSION,
        env=APP_ENV,
        hostname=HOSTNAME,
        incidents=rows,
        open_count=open_count
    )

@app.route("/api/v1/incidents", methods=["GET", "POST"])
def incidents():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if request.method == "POST":
        title = request.form.get("title") or (request.get_json(silent=True) or {}).get("title")
        severity = request.form.get("severity") or (request.get_json(silent=True) or {}).get("severity", "medium")
        if not title:
            return jsonify({"error": "title required"}), 400
        c.execute(
            "INSERT INTO incidents (title, severity, status, owner) VALUES (?, ?, 'open', ?)",
            (title, severity, request.form.get("owner") or "unassigned")
        )
        conn.commit()
        conn.close()
        log.info(f"incident created: {title} [{severity}]")
        if request.form:
            return home()
        return jsonify({"ok": True, "title": title}), 201

    c.execute("SELECT id, title, severity, status, created_at FROM incidents ORDER BY id DESC")
    data = [{"id": r[0], "title": r[1], "severity": r[2], "status": r[3], "created_at": r[4]} for r in c.fetchall()]
    conn.close()
    return jsonify({"incidents": data, "count": len(data)})

@app.route("/health/live")
def live():
    return jsonify({"status": "up", "probe": "liveness", "service": SERVICE_NAME, "ts": time.time()}), 200

@app.route("/health/ready")
def ready():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        return jsonify({
            "status": "ready",
            "probe": "readiness",
            "db": "ok",
            "version": APP_VERSION
        }), 200
    except Exception as exc:
        log.error(f"readiness failed: {exc}")
        return jsonify({"status": "down", "error": str(exc)}), 503

@app.route("/api/v1/load")
def load():
    """Simple CPU burner for HPA demos."""
    secs = float(request.args.get("s", 1.5))
    end = time.time() + secs
    while time.time() < end:
        _ = sum(i * i for i in range(800))
    return jsonify({"burned": secs, "host": HOSTNAME})

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    log.info(f"Capstone DevOps Project {APP_VERSION} starting on :5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
