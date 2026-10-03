import csv
import html
import os
from collections import Counter


EVENTS_FILE = "data/events.csv"
DASHBOARD_FILE = "reports/event-dashboard.html"


def load_events():
    """Load event records from the CSV file."""

    if not os.path.exists(EVENTS_FILE):
        print(f"Event file not found: {EVENTS_FILE}")
        return []

    events = []

    with open(
        EVENTS_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            try:
                row["duration_value"] = float(
                    row.get("duration_seconds", 0)
                    or 0
                )
            except ValueError:
                row["duration_value"] = 0.0

            try:
                row["motion_area_value"] = int(
                    float(
                        row.get("motion_area", 0)
                        or 0
                    )
                )
            except ValueError:
                row["motion_area_value"] = 0

            events.append(row)

    return events


def format_duration(seconds):
    """Make a duration easier to read."""

    if seconds < 60:
        return f"{seconds:.2f}s"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    return f"{minutes}m {remaining_seconds:.2f}s"


def evidence_link(event):
    """Return an HTML link to the event evidence image."""

    evidence_path = (
        event.get("evidence_path", "")
        or ""
    )

    if not evidence_path:
        return "None"

    filename = os.path.basename(
        evidence_path.replace("\\", "/")
    )

    if not filename:
        return "None"

    relative_path = (
        "../data/evidence/"
        + filename
    )

    safe_path = html.escape(
        relative_path,
        quote=True
    )

    return (
        f'<a href="{safe_path}" '
        f'target="_blank">View evidence</a>'
    )


def build_dashboard(events):
    """Build the complete dashboard HTML."""

    os.makedirs(
        "reports",
        exist_ok=True
    )

    total_events = len(events)

    total_duration = sum(
        event["duration_value"]
        for event in events
    )

    average_duration = (
        total_duration / total_events
        if total_events > 0
        else 0
    )

    longest_event = (
        max(
            events,
            key=lambda event: event["duration_value"]
        )
        if events
        else None
    )

    evidence_count = sum(
        1
        for event in events
        if event.get("evidence_path")
    )

    region_counts = Counter(
        event.get("region", "UNKNOWN")
        or "UNKNOWN"
        for event in events
    )

    camera_counts = Counter(
        event.get("camera_id", "UNKNOWN")
        or "UNKNOWN"
        for event in events
    )

    # Build region summary rows
    region_rows = []

    if region_counts:

        maximum_region_count = max(
            region_counts.values()
        )

        for region, count in (
            region_counts.most_common()
        ):

            percentage = (
                count / maximum_region_count
            ) * 100

            region_rows.append(
                f"""
                <div class="region-row">
                    <div class="region-name">
                        {html.escape(region)}
                    </div>

                    <div class="bar-background">
                        <div
                            class="bar"
                            style="width: {percentage:.1f}%"
                        ></div>
                    </div>

                    <div class="region-count">
                        {count}
                    </div>
                </div>
                """
            )

    # Build event table
    event_rows = []

    for event in reversed(events):

        event_id = html.escape(
            event.get("event_id", "")
        )

        camera_id = html.escape(
            event.get("camera_id", "UNKNOWN")
            or "UNKNOWN"
        )

        start_time = html.escape(
            event.get("start_time", "")
        )

        region = html.escape(
            event.get("region", "UNKNOWN")
            or "UNKNOWN"
        )

        motion_area = event[
            "motion_area_value"
        ]

        duration = format_duration(
            event["duration_value"]
        )

        evidence = evidence_link(event)

        search_text = html.escape(
            " ".join([
                event.get("event_id", ""),
                event.get("camera_id", "")
                or "UNKNOWN",
                event.get("region", "")
                or "UNKNOWN",
                event.get("start_time", ""),
            ]).lower()
        )

        event_rows.append(
            f"""
            <tr data-search="{search_text}">
                <td><code>{event_id}</code></td>
                <td>{camera_id}</td>
                <td>{start_time}</td>
                <td>{region}</td>
                <td>{motion_area}</td>
                <td>{duration}</td>
                <td>{evidence}</td>
            </tr>
            """
        )

    if longest_event:

        longest_id = html.escape(
            longest_event.get(
                "event_id",
                ""
            )
        )

        longest_camera = html.escape(
            longest_event.get(
                "camera_id",
                "UNKNOWN"
            )
            or "UNKNOWN"
        )

        longest_region = html.escape(
            longest_event.get(
                "region",
                "UNKNOWN"
            )
            or "UNKNOWN"
        )

        longest_duration = format_duration(
            longest_event["duration_value"]
        )

        longest_section = f"""
        <div class="highlight">
            <h3>Longest Event</h3>

            <p>
                <strong>ID:</strong>
                <code>{longest_id}</code>
            </p>

            <p>
                <strong>Camera:</strong>
                {longest_camera}
            </p>

            <p>
                <strong>Region:</strong>
                {longest_region}
            </p>

            <p>
                <strong>Duration:</strong>
                {longest_duration}
            </p>
        </div>
        """

    else:

        longest_section = """
        <div class="highlight">
            <h3>Longest Event</h3>
            <p>No event records available.</p>
        </div>
        """

    dashboard = f"""
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Project Sentinel - Event Dashboard</title>

    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 0;

            font-family:
                Arial,
                Helvetica,
                sans-serif;

            background: #f4f4f4;
            color: #222;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px 20px;
        }}

        header {{
            margin-bottom: 25px;
        }}

        h1 {{
            margin-bottom: 5px;
        }}

        .subtitle {{
            color: #666;
        }}

        .cards {{
            display: grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(180px, 1fr)
                );

            gap: 15px;
            margin-bottom: 25px;
        }}

        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;

            box-shadow:
                0 2px 8px
                rgba(0, 0, 0, 0.08);
        }}

        .card-title {{
            color: #666;
            font-size: 14px;
            margin-bottom: 8px;
        }}

        .card-value {{
            font-size: 28px;
            font-weight: bold;
        }}

        .section {{
            background: white;
            border-radius: 10px;
            padding: 20px;

            margin-bottom: 25px;

            box-shadow:
                0 2px 8px
                rgba(0, 0, 0, 0.08);
        }}

        .region-row {{
            display: grid;

            grid-template-columns:
                130px 1fr 50px;

            gap: 10px;

            align-items: center;

            margin-bottom: 12px;
        }}

        .region-name {{
            font-weight: bold;
        }}

        .bar-background {{
            height: 18px;

            background: #e5e5e5;

            border-radius: 10px;

            overflow: hidden;
        }}

        .bar {{
            height: 100%;
            background: #444;
        }}

        .region-count {{
            text-align: right;
            font-weight: bold;
        }}

        .highlight {{
            background: #fafafa;
            border-left: 4px solid #444;

            padding: 15px;
            margin-top: 15px;
        }}

        .search {{
            width: 100%;

            padding: 12px;

            margin-bottom: 20px;

            border:
                1px solid #ccc;

            border-radius: 6px;

            font-size: 16px;
        }}

        .table-container {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;

            border-collapse: collapse;

            min-width: 850px;
        }}

        th,
        td {{
            text-align: left;

            padding: 11px;

            border-bottom:
                1px solid #ddd;
        }}

        th {{
            background: #f0f0f0;
        }}

        code {{
            font-family:
                Consolas,
                "Courier New",
                monospace;
        }}

        a {{
            color: #333;
        }}

        footer {{
            color: #777;
            font-size: 14px;
            margin-top: 25px;
        }}

        @media (max-width: 600px) {{

            .region-row {{
                grid-template-columns:
                    100px 1fr 40px;
            }}

            .container {{
                padding: 20px 12px;
            }}

        }}

    </style>

</head>

<body>

<div class="container">

    <header>

        <h1>Project Sentinel</h1>

        <div class="subtitle">
            Event Dashboard
        </div>

        <p>
            Generated from
            <code>data/events.csv</code>.
        </p>

    </header>


    <section class="cards">

        <div class="card">

            <div class="card-title">
                Total Events
            </div>

            <div class="card-value">
                {total_events}
            </div>

        </div>


        <div class="card">

            <div class="card-title">
                Average Duration
            </div>

            <div class="card-value">
                {format_duration(average_duration)}
            </div>

        </div>


        <div class="card">

            <div class="card-title">
                Longest Event
            </div>

            <div class="card-value">
                {format_duration(
                    longest_event["duration_value"]
                ) if longest_event else "0s"}
            </div>

        </div>


        <div class="card">

            <div class="card-title">
                Evidence Linked
            </div>

            <div class="card-value">
                {evidence_count}
            </div>

        </div>

    </section>


    <section class="section">

        <h2>Events by Region</h2>

        {"".join(region_rows)
        if region_rows
        else "<p>No region data available.</p>"}

    </section>


    <section class="section">

        <h2>Camera Summary</h2>

        <p>
            {
                " · ".join(
                    f"{html.escape(camera)}: {count}"
                    for camera, count
                    in camera_counts.most_common()
                )
                if camera_counts
                else "No camera data available."
            }
        </p>

    </section>


    <section class="section">

        <h2>Event Details</h2>

        <input
            type="text"
            id="searchBox"
            class="search"
            placeholder="Search event ID, camera, region, or time..."
        >

        <div class="table-container">

            <table>

                <thead>

                    <tr>
                        <th>Event ID</th>
                        <th>Camera</th>
                        <th>Start Time</th>
                        <th>Region</th>
                        <th>Motion Area</th>
                        <th>Duration</th>
                        <th>Evidence</th>
                    </tr>

                </thead>

                <tbody id="eventTable">

                    {"".join(event_rows)
                    if event_rows
                    else
                    '<tr><td colspan="7">No events available.</td></tr>'}

                </tbody>

            </table>

        </div>

    </section>


    <section class="section">

        <h2>Notable Event</h2>

        {longest_section}

    </section>


    <footer>

        Project Sentinel — local development dashboard.

    </footer>

</div>


<script>

    const searchBox =
        document.getElementById("searchBox");

    const rows =
        document.querySelectorAll(
            "#eventTable tr"
        );

    searchBox.addEventListener(
        "input",
        function () {{

            const searchTerm =
                this.value.toLowerCase();

            rows.forEach(
                function (row) {{

                    const text =
                        row.dataset.search || "";

                    row.style.display =
                        text.includes(searchTerm)
                        ? ""
                        : "none";

                }}
            );

        }}
    );

</script>

</body>

</html>
"""

    with open(
        DASHBOARD_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(dashboard)


def main():

    events = load_events()

    if not events:
        print("No event records available.")
        return

    build_dashboard(events)

    print(
        f"Loaded {len(events)} events."
    )

    print(
        f"Dashboard saved: {DASHBOARD_FILE}"
    )


if __name__ == "__main__":
    main()