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


# ------------------------------------------------------------
# Make sure src/ can be imported
# ------------------------------------------------------------

SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


import event_dashboard


# ============================================================
# Dashboard generation
# ============================================================

def generate_dashboard():
    """
    Regenerate the dashboard from the latest event history.
    """
    event_dashboard.main()


def load_dashboard_html():
    """
    Read the generated dashboard and add a browser refresh
    instruction for live updates.

    The stored dashboard file itself is not modified by this
    function.
    """
    if not DASHBOARD_PATH.exists():
        generate_dashboard()

    with open(
        DASHBOARD_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        html = file.read()

    refresh_tag = (
        '<meta http-equiv="refresh" content="5">'
    )

    if "</head>" in html:
        html = html.replace(
            "</head>",
            f"    {refresh_tag}\n</head>",
            1
        )

    return html


# ============================================================
# HTTP handler
# ============================================================

class SentinelDashboardHandler(
    SimpleHTTPRequestHandler
):
    """
    HTTP handler for the local Sentinel dashboard.

    Every dashboard request regenerates the HTML from the
    latest events.csv before returning it to the browser.
    """

    def do_GET(self):

        request_path = self.path.split(
            "?",
            1
        )[0]

        # ----------------------------------------------------
        # Dashboard
        # ----------------------------------------------------

        if request_path in (
            "/",
            "/dashboard",
            "/dashboard/",
            "/reports/event-dashboard.html",
        ):

            try:

                generate_dashboard()

                html = load_dashboard_html()

                data = html.encode(
                    "utf-8"
                )

                self.send_response(
                    200
                )

                self.send_header(
                    "Content-Type",
                    "text/html; charset=utf-8"
                )

                self.send_header(
                    "Content-Length",
                    str(len(data))
                )

                self.send_header(
                    "Cache-Control",
                    "no-store, no-cache, must-revalidate"
                )

                self.send_header(
                    "Pragma",
                    "no-cache"
                )

                self.end_headers()

                self.wfile.write(
                    data
                )

            except Exception as error:

                message = (
                    "Dashboard generation failed:\n\n"
                    f"{type(error).__name__}: {error}"
                )

                data = message.encode(
                    "utf-8"
                )

                self.send_response(
                    500
                )

                self.send_header(
                    "Content-Type",
                    "text/plain; charset=utf-8"
                )

                self.send_header(
                    "Content-Length",
                    str(len(data))
                )

                self.end_headers()

                self.wfile.write(
                    data
                )

            return

        # ----------------------------------------------------
        # Everything else
        #
        # This allows evidence images and other project files
        # to be opened through the same local server.
        # ----------------------------------------------------

        super().do_GET()

    def log_message(
        self,
        format_string,
        *args
    ):
        """
        Keep the terminal output simple and readable.
        """
        print(
            f"[Dashboard] {format_string % args}"
        )


# ============================================================
# Main server
# ============================================================

def main():

    os.chdir(
        PROJECT_ROOT
    )

    server_address = (
        HOST,
        PORT
    )

    server = ThreadingHTTPServer(
        server_address,
        SentinelDashboardHandler
    )

    print()
    print(
        "=============================================="
    )
    print(
        " Project Sentinel - Live Dashboard"
    )
    print(
        "=============================================="
    )
    print(
        f"Project root: {PROJECT_ROOT}"
    )
    print(
        f"Server: http://{HOST}:{PORT}"
    )
    print(
        "Dashboard:"
    )
    print(
        f"http://{HOST}:{PORT}/reports/event-dashboard.html"
    )
    print()
    print(
        "The dashboard refreshes every 5 seconds."
    )
    print(
        "Press CTRL+C to stop the server."
    )
    print()

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print()
        print(
            "Stopping dashboard server..."
        )

    finally:

        server.server_close()

        print(
            "Dashboard server stopped."
        )


if __name__ == "__main__":
    main()