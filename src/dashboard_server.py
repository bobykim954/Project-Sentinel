import html
import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


# ============================================================
# Project Sentinel - Live Dashboard Server
# ============================================================

HOST = "127.0.0.1"
PORT = 8000

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_PATH = PROJECT_ROOT / "reports" / "event-dashboard.html"
ACTIVE_EVENT_PATH = PROJECT_ROOT / "data" / "active_event.json"


# ------------------------------------------------------------
# Make sure src/ can be imported
# ------------------------------------------------------------

SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import event_dashboard  # noqa: E402


# ============================================================
# Dashboard generation
# ============================================================

def generate_dashboard():
    """Regenerate the historical dashboard from events.csv."""
    event_dashboard.main()


def build_active_event_panel():
    """Build the live event panel from data/active_event.json."""
    try:
        with ACTIVE_EVENT_PATH.open("r", encoding="utf-8") as file:
            active_event = json.load(file)
    except (OSError, json.JSONDecodeError):
        active_event = None

    if not isinstance(active_event, dict) or active_event.get("status") != "ACTIVE":
        details = """
        <p id="sentinel-active-status">
            <strong>Status:</strong> Monitoring for an active person event.
            No active event is currently reported.
        </p>
        """
    else:
        def safe_text(key, fallback="UNKNOWN"):
            value = active_event.get(key, fallback)
            return html.escape(str(value if value not in (None, "") else fallback))

        event_id = safe_text("event_id")
        camera_id = safe_text("camera_id")
        start_time = safe_text("start_time")
        updated_at = safe_text("updated_at")
        region = safe_text("region")

        try:
            object_count = max(0, int(active_event.get("object_count", 0)))
        except (TypeError, ValueError):
            object_count = 0

        try:
            motion_area = max(0, int(float(active_event.get("motion_area", 0))))
        except (TypeError, ValueError):
            motion_area = 0

        try:
            confidence = float(active_event.get("detection_confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = min(1.0, max(0.0, confidence))

        try:
            elapsed_seconds = max(0.0, float(active_event.get("elapsed_seconds", 0.0)))
        except (TypeError, ValueError):
            elapsed_seconds = 0.0

        evidence_filename = os.path.basename(
            str(active_event.get("evidence_path", "")).replace("\\", "/")
        )
        evidence_html = ""
        if evidence_filename and evidence_filename not in (".", ".."):
            safe_filename = html.escape(evidence_filename, quote=True)
            evidence_html = (
                '<p><a href="../data/evidence/'
                f'{safe_filename}" target="_blank" rel="noopener">'
                "Open event evidence snapshot</a></p>"
            )

        details = f"""
        <p id="sentinel-active-status" style="font-size: 1.05rem;">
            <strong style="color: #b91c1c;">● ACTIVE NOW</strong>
        </p>
        <div class="sentinel-active-grid">
            <div><strong>Event ID</strong><br>{event_id}</div>
            <div><strong>Camera</strong><br>{camera_id}</div>
            <div><strong>Primary region so far</strong><br>{region}</div>
            <div><strong>Maximum people detected</strong><br>{object_count}</div>
            <div><strong>Maximum detection confidence</strong><br>{confidence:.2f}</div>
            <div><strong>Latest motion area</strong><br>{motion_area} pixels</div>
            <div><strong>Elapsed time</strong><br>{elapsed_seconds:.1f} seconds</div>
            <div><strong>Started at</strong><br>{start_time}</div>
        </div>
        {evidence_html}
        <p class="sentinel-active-updated">Last status update: {updated_at}</p>
        """

    return f"""
    <section id="sentinel-live-event" aria-live="polite" style="
        margin: 20px 0;
        padding: 20px;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        background: #f8fafc;
        color: #0f172a;
        overflow-wrap: anywhere;
    ">
        <h2 style="margin-top: 0;">Live Event Monitor</h2>
        <style>
            .sentinel-active-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                gap: 14px;
            }}
            .sentinel-active-updated {{ font-size: 0.85rem; margin-bottom: 0; }}
        </style>
        {details}
    </section>
    """


def load_dashboard_html():
    """Load the generated dashboard and inject live status and refresh metadata."""
    if not DASHBOARD_PATH.exists():
        generate_dashboard()

    with DASHBOARD_PATH.open("r", encoding="utf-8") as file:
        page_html = file.read()

    refresh_tag = '<meta http-equiv="refresh" content="5">'
    if "</head>" in page_html and refresh_tag not in page_html:
        page_html = page_html.replace(
            "</head>", f"    {refresh_tag}\n</head>", 1
        )

    active_panel = build_active_event_panel()
    if "</header>" in page_html:
        page_html = page_html.replace("</header>", "</header>\n" + active_panel, 1)
    elif "</body>" in page_html:
        page_html = page_html.replace("</body>", active_panel + "\n</body>", 1)

    return page_html


# ============================================================
# HTTP handler
# ============================================================

class SentinelDashboardHandler(SimpleHTTPRequestHandler):
    """Serve the refreshed dashboard, evidence files, and other project files."""

    def do_GET(self):
        request_path = self.path.split("?", 1)[0]

        if request_path in ("/", "/dashboard", "/dashboard/", "/reports/event-dashboard.html"):
            try:
                generate_dashboard()
                page_html = load_dashboard_html()
                data = page_html.encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.end_headers()
                self.wfile.write(data)
            except Exception as error:
                message = f"Dashboard generation failed:\n\n{type(error).__name__}: {error}"
                data = message.encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
            return

        # The standard handler serves event evidence and other project files.
        super().do_GET()

    def log_message(self, format_string, *args):
        print(f"[Dashboard] {format_string % args}")


# ============================================================
# Main server
# ============================================================

def main():
    os.chdir(PROJECT_ROOT)
    server_address = (HOST, PORT)
    server = ThreadingHTTPServer(server_address, SentinelDashboardHandler)

    print()
    print("==============================================")
    print(" Project Sentinel - Live Dashboard")
    print("==============================================")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Server: http://{HOST}:{PORT}")
    print(f"Dashboard: http://{HOST}:{PORT}/reports/event-dashboard.html")
    print("The dashboard refreshes every 5 seconds.")
    print("Press CTRL+C to stop the server.")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server...")
    finally:
        server.server_close()
        print("Dashboard server stopped.")


if __name__ == "__main__":
    main()