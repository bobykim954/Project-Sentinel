import html
import os
from collections import Counter
from datetime import datetime

from event_priority import (
    calculate_priority,
    get_priority_reason,
    is_multi_person_event,
    load_events,
)


EVENTS_FILE = "data/events.csv"
DASHBOARD_FILE = "reports/event-dashboard.html"


# ============================================================
# Utility functions
# ============================================================

def format_duration(seconds):
    """
    Format event duration for easier reading.
    """
    if seconds < 60:
        return f"{seconds:.2f}s"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    return f"{minutes}m {remaining_seconds:.2f}s"


def get_object_type(event):
    """
    Return a readable object type.
    """
    object_type = (
        event.get("object_type", "")
        or ""
    ).strip().upper()

    return object_type if object_type else "UNKNOWN"


def get_object_count(event):
    """
    Return stored object count as an integer.
    """
    try:
        return int(
            float(
                event.get("object_count", 0)
                or 0
            )
        )
    except (ValueError, TypeError):
        return 0


def get_confidence(event):
    """
    Return stored detection confidence.
    """
    try:
        return float(
            event.get("detection_confidence", 0)
            or 0
        )
    except (ValueError, TypeError):
        return 0.0


def evidence_link(event):
    """
    Create a safe link to the event evidence image.
    """
    evidence_path = (
        event.get("evidence_path", "")
        or ""
    )

    if not evidence_path:
        return "None"

    normalized_path = evidence_path.replace(
        "\\",
        "/"
    )

    filename = os.path.basename(
        normalized_path
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
        f'<a class="evidence-link" '
        f'href="{safe_path}" '
        f'target="_blank">View evidence</a>'
    )


def priority_class(priority):
    """
    Convert priority into a CSS class.
    """
    return priority.lower()


# ============================================================
# Dashboard generation
# ============================================================

def build_dashboard(events):
    """
    Build the complete local HTML dashboard.
    """
    os.makedirs(
        "reports",
        exist_ok=True
    )

    # --------------------------------------------------------
    # Basic statistics
    # --------------------------------------------------------

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

    evidence_count = sum(
        1
        for event in events
        if event.get("evidence_path")
    )

    person_events = [
        event
        for event in events
        if get_object_type(event) == "PERSON"
    ]

    multi_person_events = [
        event
        for event in events
        if is_multi_person_event(event)
    ]

    # --------------------------------------------------------
    # Calculate priorities using Day 16 engine
    # --------------------------------------------------------

    priority_counts = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
    }

    for event in events:
        event["dashboard_priority"] = (
            calculate_priority(event)
        )

        event["dashboard_reason"] = (
            get_priority_reason(event)
        )

        priority_counts[
            event["dashboard_priority"]
        ] += 1

    # --------------------------------------------------------
    # Region / camera summaries
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Latest / notable events
    # --------------------------------------------------------

    newest_event = (
        events[-1]
        if events
        else None
    )

    longest_event = (
        max(
            events,
            key=lambda event: event[
                "duration_value"
            ]
        )
        if events
        else None
    )

    highest_priority_events = [
        event
        for event in events
        if event["dashboard_priority"] == "HIGH"
    ]

    newest_high_event = (
        highest_priority_events[-1]
        if highest_priority_events
        else None
    )

    # --------------------------------------------------------
    # Region rows
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Camera rows
    # --------------------------------------------------------

    camera_rows = []

    for camera, count in camera_counts.most_common():

        camera_rows.append(
            f"""
            <div class="camera-item">
                <span>
                    {html.escape(camera)}
                </span>

                <strong>
                    {count}
                </strong>
            </div>
            """
        )

    # --------------------------------------------------------
    # Event table
    # --------------------------------------------------------

    event_rows = []

    # Newest first
    for event in reversed(events):

        event_id = html.escape(
            event.get("event_id", "")
        )

        camera_id = html.escape(
            event.get(
                "camera_id",
                "UNKNOWN"
            )
            or "UNKNOWN"
        )

        start_time = html.escape(
            event.get("start_time", "")
        )

        region_value = (
            event.get("region", "UNKNOWN")
            or "UNKNOWN"
        )

        region = html.escape(
            region_value
        )

        motion_area = event[
            "motion_area_value"
        ]

        duration_value = event[
            "duration_value"
        ]

        duration = format_duration(
            duration_value
        )

        object_type_value = (
            get_object_type(event)
        )

        object_type = html.escape(
            object_type_value
        )

        object_count_value = (
            get_object_count(event)
        )

        object_count = (
            str(object_count_value)
            if object_count_value > 0
            else "-"
        )

        confidence_value = (
            get_confidence(event)
        )

        confidence = (
            f"{confidence_value:.2f}"
            if confidence_value > 0
            else "-"
        )

        priority = event[
            "dashboard_priority"
        ]

        reason = html.escape(
            event["dashboard_reason"]
        )

        evidence = evidence_link(event)

        # ----------------------------------------------------
        # Search/filter attributes
        # ----------------------------------------------------

        search_text = html.escape(
            " ".join([
                event.get(
                    "event_id",
                    ""
                ),
                event.get(
                    "camera_id",
                    ""
                ) or "UNKNOWN",
                region_value,
                object_type_value,
                event.get(
                    "start_time",
                    ""
                ),
                priority,
                reason,
            ]).lower()
        )

        filter_object = html.escape(
            object_type_value
        )

        filter_region = html.escape(
            region_value
        )

        event_rows.append(
            f"""
            <tr
                data-search="{search_text}"
                data-priority="{priority}"
                data-object="{filter_object}"
                data-region="{filter_region}"
            >
                <td>
                    <code>{event_id}</code>
                </td>

                <td>
                    {camera_id}
                </td>

                <td>
                    {start_time}
                </td>

                <td>
                    {region}
                </td>

                <td>
                    {object_type}
                </td>

                <td>
                    {object_count}
                </td>

                <td>
                    {confidence}
                </td>

                <td>
                    <span class="priority {priority_class(priority)}">
                        {priority}
                    </span>
                </td>

                <td>
                    {motion_area}
                </td>

                <td>
                    {duration}
                </td>

                <td>
                    {evidence}
                </td>

                <td>
                    <span
                        class="reason"
                        title="{reason}"
                    >
                        {reason}
                    </span>
                </td>
            </tr>
            """
        )

    # --------------------------------------------------------
    # Latest event section
    # --------------------------------------------------------

    if newest_event:

        newest_id = html.escape(
            newest_event.get(
                "event_id",
                ""
            )
        )

        newest_camera = html.escape(
            newest_event.get(
                "camera_id",
                "UNKNOWN"
            )
            or "UNKNOWN"
        )

        newest_region = html.escape(
            newest_event.get(
                "region",
                "UNKNOWN"
            )
            or "UNKNOWN"
        )

        newest_time = html.escape(
            newest_event.get(
                "start_time",
                ""
            )
        )

        newest_object = html.escape(
            get_object_type(newest_event)
        )

        newest_count = (
            get_object_count(newest_event)
        )

        newest_confidence = (
            get_confidence(newest_event)
        )

        newest_priority = (
            newest_event["dashboard_priority"]
        )

        newest_reason = html.escape(
            newest_event["dashboard_reason"]
        )

        newest_evidence = evidence_link(
            newest_event
        )

        latest_section = f"""
        <div class="highlight">
            <div class="highlight-header">
                <h3>Latest Event</h3>

                <span class="priority {priority_class(newest_priority)}">
                    {newest_priority}
                </span>
            </div>

            <div class="detail-grid">

                <div>
                    <span class="detail-label">
                        Event ID
                    </span>

                    <code>
                        {newest_id}
                    </code>
                </div>

                <div>
                    <span class="detail-label">
                        Time
                    </span>

                    {newest_time}
                </div>

                <div>
                    <span class="detail-label">
                        Camera
                    </span>

                    {newest_camera}
                </div>

                <div>
                    <span class="detail-label">
                        Region
                    </span>

                    {newest_region}
                </div>

                <div>
                    <span class="detail-label">
                        Object
                    </span>

                    {newest_object}
                </div>

                <div>
                    <span class="detail-label">
                        People
                    </span>

                    {
                        newest_count
                        if newest_count > 0
                        else "-"
                    }
                </div>

                <div>
                    <span class="detail-label">
                        Confidence
                    </span>

                    {
                        f"{newest_confidence:.2f}"
                        if newest_confidence > 0
                        else "-"
                    }
                </div>

                <div>
                    <span class="detail-label">
                        Evidence
                    </span>

                    {newest_evidence}
                </div>

            </div>

            <div class="reason-box">
                <strong>Priority reason:</strong>
                {newest_reason}
            </div>
        </div>
        """

    else:

        latest_section = """
        <div class="highlight">
            <h3>Latest Event</h3>
            <p>No event records available.</p>
        </div>
        """

    # --------------------------------------------------------
    # Longest event section
    # --------------------------------------------------------

    if longest_event:

        longest_id = html.escape(
            longest_event.get(
                "event_id",
                ""
            )
        )

        longest_duration = format_duration(
            longest_event[
                "duration_value"
            ]
        )

        longest_priority = (
            longest_event["dashboard_priority"]
        )

        longest_reason = html.escape(
            longest_event["dashboard_reason"]
        )

        longest_section = f"""
        <div class="mini-highlight">
            <h3>Longest Event</h3>

            <p>
                <strong>ID:</strong>
                <code>{longest_id}</code>
            </p>

            <p>
                <strong>Duration:</strong>
                {longest_duration}
            </p>

            <p>
                <strong>Priority:</strong>

                <span class="priority {priority_class(longest_priority)}">
                    {longest_priority}
                </span>
            </p>

            <p>
                <strong>Reason:</strong>
                {longest_reason}
            </p>
        </div>
        """

    else:

        longest_section = """
        <div class="mini-highlight">
            <h3>Longest Event</h3>
            <p>No event records available.</p>
        </div>
        """

    # --------------------------------------------------------
    # Newest high priority section
    # --------------------------------------------------------

    if newest_high_event:

        high_id = html.escape(
            newest_high_event.get(
                "event_id",
                ""
            )
        )

        high_time = html.escape(
            newest_high_event.get(
                "start_time",
                ""
            )
        )

        high_reason = html.escape(
            newest_high_event[
                "dashboard_reason"
            ]
        )

        high_section = f"""
        <div class="mini-highlight">
            <h3>Latest High Priority Event</h3>

            <p>
                <strong>ID:</strong>
                <code>{high_id}</code>
            </p>

            <p>
                <strong>Time:</strong>
                {high_time}
            </p>

            <p>
                <strong>Reason:</strong>
                {high_reason}
            </p>
        </div>
        """

    else:

        high_section = """
        <div class="mini-highlight">
            <h3>Latest High Priority Event</h3>
            <p>No high-priority events available.</p>
        </div>
        """

    # --------------------------------------------------------
    # Generate timestamp
    # --------------------------------------------------------

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # --------------------------------------------------------
    # Complete dashboard HTML
    # --------------------------------------------------------

    dashboard = f"""
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        Project Sentinel - Event Dashboard
    </title>

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
            max-width: 1450px;
            margin: 0 auto;
            padding: 30px 20px;
        }}

        header {{
            margin-bottom: 25px;
        }}

        h1 {{
            margin:
                0 0 5px
                0;
        }}

        h2 {{
            margin-top: 0;
        }}

        h3 {{
            margin-top: 0;
        }}

        .subtitle {{
            color: #666;
        }}

        .muted {{
            color: #777;
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

        .summary-grid {{
            display: grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(260px, 1fr)
                );

            gap: 20px;
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

        .camera-list {{
            display: grid;

            gap: 10px;
        }}

        .camera-item {{
            display: flex;

            justify-content: space-between;

            padding:
                10px 12px;

            border:
                1px solid #ddd;

            border-radius: 6px;

            background: #fafafa;
        }}

        .priority-bars {{
            display: grid;

            gap: 12px;
        }}

        .priority-row {{
            display: grid;

            grid-template-columns:
                80px 1fr 40px;

            gap: 10px;

            align-items: center;
        }}

        .priority-name {{
            font-weight: bold;
        }}

        .priority-bar-background {{
            height: 18px;

            background: #e5e5e5;

            border-radius: 10px;

            overflow: hidden;
        }}

        .priority-bar {{
            height: 100%;
        }}

        .priority-bar.high {{
            background: #b33;
        }}

        .priority-bar.medium {{
            background: #777;
        }}

        .priority-bar.low {{
            background: #aaa;
        }}

        .priority {{
            display: inline-block;

            padding:
                4px 8px;

            border-radius: 5px;

            font-size: 12px;

            font-weight: bold;
        }}

        .priority.high {{
            background: #f1cccc;
            color: #7f0000;
        }}

        .priority.medium {{
            background: #e7e7e7;
            color: #333;
        }}

        .priority.low {{
            background: #f2f2f2;
            color: #666;
        }}

        .highlight {{
            background: #fafafa;

            border-left:
                4px solid #444;

            padding: 20px;

            margin-top: 15px;
        }}

        .highlight-header {{
            display: flex;

            justify-content: space-between;

            align-items: center;

            gap: 15px;

            margin-bottom: 15px;
        }}

        .detail-grid {{
            display: grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(190px, 1fr)
                );

            gap: 15px;
        }}

        .detail-grid > div {{
            padding: 10px;

            background: white;

            border:
                1px solid #ddd;

            border-radius: 6px;
        }}

        .detail-label {{
            display: block;

            color: #777;

            font-size: 12px;

            margin-bottom: 5px;
        }}

        .reason-box {{
            margin-top: 15px;

            padding: 12px;

            background: white;

            border:
                1px solid #ddd;

            border-radius: 6px;
        }}

        .mini-grid {{
            display: grid;

            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(280px, 1fr)
                );

            gap: 20px;
        }}

        .mini-highlight {{
            background: #fafafa;

            border:
                1px solid #ddd;

            border-radius: 8px;

            padding: 18px;
        }}

        .filters {{
            display: grid;

            grid-template-columns:
                2fr
                1fr
                1fr
                1fr;

            gap: 12px;

            margin-bottom: 20px;
        }}

        .filter-input,
        .filter-select {{
            width: 100%;

            padding: 11px;

            border:
                1px solid #ccc;

            border-radius: 6px;

            font-size: 14px;

            background: white;
        }}

        .table-container {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;

            border-collapse:
                collapse;

            min-width: 1350px;
        }}

        th,
        td {{
            text-align: left;

            padding: 11px;

            border-bottom:
                1px solid #ddd;

            vertical-align: top;
        }}

        th {{
            background: #f0f0f0;

            position: sticky;

            top: 0;

            z-index: 1;
        }}

        tbody tr:hover {{
            background: #fafafa;
        }}

        code {{
            font-family:
                Consolas,
                "Courier New",
                monospace;

            font-size: 12px;
        }}

        .evidence-link {{
            color: #333;

            font-weight: bold;

            text-decoration: none;
        }}

        .evidence-link:hover {{
            text-decoration: underline;
        }}

        .reason {{
            display: inline-block;

            max-width: 320px;

            color: #555;

            line-height: 1.4;
        }}

        .empty-row {{
            text-align: center;

            color: #777;

            padding: 25px;
        }}

        footer {{
            color: #777;

            font-size: 14px;

            margin-top: 25px;
        }}

        @media (max-width: 900px) {{

            .filters {{
                grid-template-columns:
                    1fr;
            }}

        }}

        @media (max-width: 600px) {{

            .container {{
                padding:
                    20px 12px;
            }}

            .region-row {{
                grid-template-columns:
                    100px 1fr 40px;
            }}

        }}

    </style>

</head>


<body>

<div class="container">

    <header>

        <h1>
            Project Sentinel
        </h1>

        <div class="subtitle">
            Event Intelligence Dashboard
        </div>

        <p class="muted">
            Generated from
            <code>data/events.csv</code>.
        </p>

        <p class="muted">
            Last generated:
            {generated_at}
        </p>

    </header>


    <!-- =====================================================
         Main summary cards
         ===================================================== -->

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
                Person Events
            </div>

            <div class="card-value">
                {len(person_events)}
            </div>

        </div>


        <div class="card">

            <div class="card-title">
                Multi-Person Events
            </div>

            <div class="card-value">
                {len(multi_person_events)}
            </div>

        </div>


        <div class="card">

            <div class="card-title">
                High Priority
            </div>

            <div class="card-value">
                {priority_counts["HIGH"]}
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


        <div class="card">

            <div class="card-title">
                Average Duration
            </div>

            <div class="card-value">
                {format_duration(average_duration)}
            </div>

        </div>

    </section>


    <!-- =====================================================
         Analysis summaries
         ===================================================== -->

    <section class="section">

        <h2>
            Event Overview
        </h2>

        <div class="summary-grid">

            <div>

                <h3>
                    Priority Distribution
                </h3>

                <div class="priority-bars">

                    <div class="priority-row">

                        <div class="priority-name">
                            HIGH
                        </div>

                        <div class="priority-bar-background">

                            <div
                                class="priority-bar high"
                                style="
                                    width:
                                    {
                                        (
                                            priority_counts["HIGH"]
                                            / max(priority_counts.values())
                                            * 100
                                        )
                                        if max(priority_counts.values()) > 0
                                        else 0
                                    }%;
                                "
                            ></div>

                        </div>

                        <strong>
                            {priority_counts["HIGH"]}
                        </strong>

                    </div>


                    <div class="priority-row">

                        <div class="priority-name">
                            MEDIUM
                        </div>

                        <div class="priority-bar-background">

                            <div
                                class="priority-bar medium"
                                style="
                                    width:
                                    {
                                        (
                                            priority_counts["MEDIUM"]
                                            / max(priority_counts.values())
                                            * 100
                                        )
                                        if max(priority_counts.values()) > 0
                                        else 0
                                    }%;
                                "
                            ></div>

                        </div>

                        <strong>
                            {priority_counts["MEDIUM"]}
                        </strong>

                    </div>


                    <div class="priority-row">

                        <div class="priority-name">
                            LOW
                        </div>

                        <div class="priority-bar-background">

                            <div
                                class="priority-bar low"
                                style="
                                    width:
                                    {
                                        (
                                            priority_counts["LOW"]
                                            / max(priority_counts.values())
                                            * 100
                                        )
                                        if max(priority_counts.values()) > 0
                                        else 0
                                    }%;
                                "
                            ></div>

                        </div>

                        <strong>
                            {priority_counts["LOW"]}
                        </strong>

                    </div>

                </div>

            </div>


            <div>

                <h3>
                    Events by Region
                </h3>

                {
                    "".join(region_rows)
                    if region_rows
                    else
                    "<p class='muted'>No region data available.</p>"
                }

            </div>


            <div>

                <h3>
                    Camera Summary
                </h3>

                <div class="camera-list">

                    {
                        "".join(camera_rows)
                        if camera_rows
                        else
                        "<p class='muted'>No camera data available.</p>"
                    }

                </div>

            </div>

        </div>

    </section>


    <!-- =====================================================
         Notable events
         ===================================================== -->

    <section class="section">

        <h2>
            Notable Events
        </h2>

        <div class="mini-grid">

            {latest_section}

            {longest_section}

            {high_section}

        </div>

    </section>


    <!-- =====================================================
         Event table
         ===================================================== -->

    <section class="section">

        <h2>
            Event History
        </h2>

        <div class="filters">

            <input
                type="text"
                id="searchBox"
                class="filter-input"
                placeholder="
                    Search event ID, camera, region,
                    object, priority, or reason...
                "
            >

            <select
                id="priorityFilter"
                class="filter-select"
            >

                <option value="">
                    All priorities
                </option>

                <option value="HIGH">
                    HIGH
                </option>

                <option value="MEDIUM">
                    MEDIUM
                </option>

                <option value="LOW">
                    LOW
                </option>

            </select>


            <select
                id="objectFilter"
                class="filter-select"
            >

                <option value="">
                    All objects
                </option>

                <option value="PERSON">
                    PERSON
                </option>

                <option value="UNKNOWN">
                    UNKNOWN
                </option>

            </select>


            <select
                id="regionFilter"
                class="filter-select"
            >

                <option value="">
                    All regions
                </option>

                {
                    "".join(
                        f'<option value="{html.escape(region)}">'
                        f'{html.escape(region)}'
                        f'</option>'
                        for region in region_counts
                    )
                }

            </select>

        </div>


        <div class="table-container">

            <table>

                <thead>

                    <tr>

                        <th>
                            Event ID
                        </th>

                        <th>
                            Camera
                        </th>

                        <th>
                            Start Time
                        </th>

                        <th>
                            Region
                        </th>

                        <th>
                            Object
                        </th>

                        <th>
                            Count
                        </th>

                        <th>
                            Confidence
                        </th>

                        <th>
                            Priority
                        </th>

                        <th>
                            Motion Area
                        </th>

                        <th>
                            Duration
                        </th>

                        <th>
                            Evidence
                        </th>

                        <th>
                            Priority Reason
                        </th>

                    </tr>

                </thead>


                <tbody id="eventTable">

                    {
                        "".join(event_rows)
                        if event_rows
                        else
                        '''
                        <tr>
                            <td
                                colspan="12"
                                class="empty-row"
                            >
                                No events available.
                            </td>
                        </tr>
                        '''
                    }

                </tbody>

            </table>

        </div>

    </section>


    <!-- =====================================================
         Notes
         ===================================================== -->

    <section class="section">

        <h2>
            Dashboard Notes
        </h2>

        <p>
            This dashboard reads the stored event history
            generated by Project Sentinel.
        </p>

        <p>
            Priority values are calculated using the same
            rule-based priority engine used by
            <code>src/event_priority.py</code>.
        </p>

        <p>
            Historical events created before person detection
            was added may show <strong>UNKNOWN</strong> for
            object information.
        </p>

        <p>
            Evidence links point to locally stored images
            under <code>data/evidence/</code>.
        </p>

        <p>
            The dashboard is a local development interface.
            It does not claim that a HIGH priority event
            represents an intruder, crime, or dangerous
            activity.
        </p>

    </section>


    <footer>
        Project Sentinel - local event intelligence dashboard.
    </footer>

</div>


<script>

    const searchBox =
        document.getElementById(
            "searchBox"
        );


    const priorityFilter =
        document.getElementById(
            "priorityFilter"
        );


    const objectFilter =
        document.getElementById(
            "objectFilter"
        );


    const regionFilter =
        document.getElementById(
            "regionFilter"
        );


    const rows =
        document.querySelectorAll(
            "#eventTable tr"
        );


    function applyFilters() {{

        const searchTerm =
            searchBox.value
                .toLowerCase()
                .trim();


        const selectedPriority =
            priorityFilter.value;


        const selectedObject =
            objectFilter.value;


        const selectedRegion =
            regionFilter.value;


        rows.forEach(
            function(row) {{

                const text =
                    row.dataset.search || "";


                const priority =
                    row.dataset.priority || "";


                const objectType =
                    row.dataset.object || "";


                const region =
                    row.dataset.region || "";


                const matchesSearch =
                    text.includes(
                        searchTerm
                    );


                const matchesPriority =
                    !selectedPriority
                    ||
                    priority === selectedPriority;


                const matchesObject =
                    !selectedObject
                    ||
                    objectType === selectedObject;


                const matchesRegion =
                    !selectedRegion
                    ||
                    region === selectedRegion;


                row.style.display =
                    matchesSearch
                    &&
                    matchesPriority
                    &&
                    matchesObject
                    &&
                    matchesRegion
                    ? ""
                    : "none";

            }}
        );

    }}


    searchBox.addEventListener(
        "input",
        applyFilters
    );


    priorityFilter.addEventListener(
        "change",
        applyFilters
    );


    objectFilter.addEventListener(
        "change",
        applyFilters
    );


    regionFilter.addEventListener(
        "change",
        applyFilters
    );

</script>


</body>

</html>
"""

    # --------------------------------------------------------
    # Save dashboard
    # --------------------------------------------------------

    with open(
        DASHBOARD_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(dashboard)


# ============================================================
# Main
# ============================================================

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