import csv
import os
from collections import Counter
from datetime import datetime


EVENTS_FILE = "data/events.csv"
REPORT_FILE = "reports/event-summary.md"


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
                duration = float(
                    row.get("duration_seconds", 0)
                    or 0
                )
            except ValueError:
                duration = 0.0

            try:
                motion_area = int(
                    float(
                        row.get("motion_area", 0)
                        or 0
                    )
                )
            except ValueError:
                motion_area = 0

            row["duration_value"] = duration
            row["motion_area_value"] = motion_area

            events.append(row)

    return events


def build_summary(events):
    """Calculate useful statistics from the event history."""

    if not events:
        return None

    total_events = len(events)

    total_duration = sum(
        event["duration_value"]
        for event in events
    )

    average_duration = (
        total_duration / total_events
    )

    longest_event = max(
        events,
        key=lambda event: event["duration_value"]
    )

    largest_motion = max(
        events,
        key=lambda event: event["motion_area_value"]
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

    evidence_count = 0

    for event in events:

        evidence_path = (
            event.get("evidence_path", "")
            or ""
        )

        if evidence_path:
            evidence_count += 1

    latest_event = max(
        events,
        key=lambda event: event.get(
            "start_time",
            ""
        )
    )

    return {
        "total_events": total_events,
        "total_duration": total_duration,
        "average_duration": average_duration,
        "longest_event": longest_event,
        "largest_motion": largest_motion,
        "region_counts": region_counts,
        "camera_counts": camera_counts,
        "evidence_count": evidence_count,
        "latest_event": latest_event
    }


def create_report(events, summary):
    """Create the human-readable Markdown report."""

    os.makedirs(
        "reports",
        exist_ok=True
    )

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    report = []

    report.append("# Project Sentinel - Event Summary")
    report.append("")
    report.append(
        f"**Generated:** {now}"
    )
    report.append("")
    report.append(
        "This report is generated from "
        "`data/events.csv`."
    )
    report.append("")

    report.append("## Overview")
    report.append("")
    report.append(
        f"- Total events: "
        f"{summary['total_events']}"
    )
    report.append(
        f"- Total recorded duration: "
        f"{summary['total_duration']:.2f} seconds"
    )
    report.append(
        f"- Average event duration: "
        f"{summary['average_duration']:.2f} seconds"
    )
    report.append(
        f"- Evidence-linked events: "
        f"{summary['evidence_count']}"
    )
    report.append("")

    longest = summary["longest_event"]

    report.append("## Longest Event")
    report.append("")
    report.append(
        f"- Event ID: "
        f"`{longest.get('event_id', 'UNKNOWN')}`"
    )
    report.append(
        f"- Camera: "
        f"{longest.get('camera_id', 'UNKNOWN')}"
    )
    report.append(
        f"- Region: "
        f"{longest.get('region', 'UNKNOWN')}"
    )
    report.append(
        f"- Duration: "
        f"{longest['duration_value']:.2f} seconds"
    )
    report.append("")

    largest = summary["largest_motion"]

    report.append("## Largest Motion Area")
    report.append("")
    report.append(
        f"- Event ID: "
        f"`{largest.get('event_id', 'UNKNOWN')}`"
    )
    report.append(
        f"- Camera: "
        f"{largest.get('camera_id', 'UNKNOWN')}"
    )
    report.append(
        f"- Region: "
        f"{largest.get('region', 'UNKNOWN')}"
    )
    report.append(
        f"- Motion area: "
        f"{largest['motion_area_value']}"
    )
    report.append("")

    report.append("## Events by Region")
    report.append("")
    report.append(
        "| Region | Events |"
    )
    report.append(
        "|---|---:|"
    )

    for region, count in summary[
        "region_counts"
    ].most_common():

        report.append(
            f"| {region} | {count} |"
        )

    report.append("")

    report.append("## Events by Camera")
    report.append("")
    report.append(
        "| Camera | Events |"
    )
    report.append(
        "|---|---:|"
    )

    for camera, count in summary[
        "camera_counts"
    ].most_common():

        report.append(
            f"| {camera} | {count} |"
        )

    report.append("")

    latest = summary["latest_event"]

    report.append("## Latest Event")
    report.append("")
    report.append(
        f"- Event ID: "
        f"`{latest.get('event_id', 'UNKNOWN')}`"
    )
    report.append(
        f"- Camera: "
        f"{latest.get('camera_id', 'UNKNOWN')}"
    )
    report.append(
        f"- Start time: "
        f"{latest.get('start_time', 'UNKNOWN')}"
    )
    report.append(
        f"- Region: "
        f"{latest.get('region', 'UNKNOWN')}"
    )
    report.append(
        f"- Duration: "
        f"{latest['duration_value']:.2f} seconds"
    )
    report.append("")

    report.append("## Event Records")
    report.append("")
    report.append(
        "| Event ID | Camera | Region | "
        "Area | Duration | Evidence |"
    )
    report.append(
        "|---|---|---|---:|---:|---|"
    )

    for event in events:

        evidence = (
            "Yes"
            if event.get("evidence_path")
            else "No"
        )

        report.append(
            f"| `{event.get('event_id', '')}` | "
            f"{event.get('camera_id', '')} | "
            f"{event.get('region', '')} | "
            f"{event['motion_area_value']} | "
            f"{event['duration_value']:.2f}s | "
            f"{evidence} |"
        )

    report.append("")

    report.append("## Notes")
    report.append("")
    report.append(
        "This is an early analytics layer. "
        "The current statistics describe the "
        "stored motion events; they do not yet "
        "identify objects such as people or vehicles."
    )
    report.append("")

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(report)
        )


def main():

    events = load_events()

    if not events:
        print("No event records available.")
        return

    summary = build_summary(events)

    create_report(
        events,
        summary
    )

    print(
        f"Loaded {summary['total_events']} events."
    )

    print(
        f"Average duration: "
        f"{summary['average_duration']:.2f}s"
    )

    print(
        f"Longest event: "
        f"{summary['longest_event']['duration_value']:.2f}s"
    )

    print(
        f"Evidence-linked events: "
        f"{summary['evidence_count']}"
    )

    print(
        f"Report saved: {REPORT_FILE}"
    )


if __name__ == "__main__":
    main()