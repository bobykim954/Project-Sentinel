import csv
import os


EVENTS_FILE = "data/events.csv"
REPORT_FILE = "reports/event-priority.md"


HIGH_MOTION_AREA = 3000
HIGH_DURATION = 10.0

MEDIUM_MOTION_AREA = 1500
MEDIUM_DURATION = 3.0


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
                row["motion_area_value"] = int(
                    float(
                        row.get("motion_area", 0)
                        or 0
                    )
                )
            except ValueError:
                row["motion_area_value"] = 0

            try:
                row["duration_value"] = float(
                    row.get("duration_seconds", 0)
                    or 0
                )
            except ValueError:
                row["duration_value"] = 0.0

            events.append(row)

    return events


def calculate_priority(event):
    """
    Assign a simple priority using motion area
    and event duration.

    This is a rule-based prototype, not an AI score.
    """

    motion_area = event["motion_area_value"]
    duration = event["duration_value"]

    if (
        motion_area >= HIGH_MOTION_AREA
        or duration >= HIGH_DURATION
    ):
        return "HIGH"

    if (
        motion_area >= MEDIUM_MOTION_AREA
        or duration >= MEDIUM_DURATION
    ):
        return "MEDIUM"

    return "LOW"


def build_report(events):
    """Create a priority report from stored events."""

    os.makedirs(
        "reports",
        exist_ok=True
    )

    priority_counts = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }

    priority_events = []

    for event in events:

        priority = calculate_priority(event)

        event["priority"] = priority

        priority_counts[priority] += 1

        priority_events.append(event)

    priority_events.reverse()

    high_events = [
        event
        for event in priority_events
        if event["priority"] == "HIGH"
    ]

    report = []

    report.append("# Project Sentinel - Event Priority")
    report.append("")
    report.append(
        "This report applies a simple rule-based "
        "priority to the stored events."
    )
    report.append("")
    report.append(
        "The priority is based on detected motion "
        "area and event duration."
    )
    report.append("")

    report.append("## Current Rules")
    report.append("")
    report.append(
        f"- HIGH: motion area >= "
        f"{HIGH_MOTION_AREA} "
        f"or duration >= "
        f"{HIGH_DURATION:.0f}s"
    )
    report.append(
        f"- MEDIUM: motion area >= "
        f"{MEDIUM_MOTION_AREA} "
        f"or duration >= "
        f"{MEDIUM_DURATION:.0f}s"
    )
    report.append(
        "- LOW: everything else"
    )
    report.append("")

    report.append("## Priority Summary")
    report.append("")
    report.append("| Priority | Events |")
    report.append("|---|---:|")

    report.append(
        f"| HIGH | {priority_counts['HIGH']} |"
    )

    report.append(
        f"| MEDIUM | {priority_counts['MEDIUM']} |"
    )

    report.append(
        f"| LOW | {priority_counts['LOW']} |"
    )

    report.append("")

    report.append("## Events")
    report.append("")
    report.append(
        "| Event ID | Camera | Region | "
        "Area | Duration | Priority |"
    )
    report.append(
        "|---|---|---|---:|---:|---|"
    )

    for event in priority_events:

        report.append(
            f"| `{event.get('event_id', '')}` | "
            f"{event.get('camera_id', 'UNKNOWN')} | "
            f"{event.get('region', 'UNKNOWN')} | "
            f"{event['motion_area_value']} | "
            f"{event['duration_value']:.2f}s | "
            f"**{event['priority']}** |"
        )

    report.append("")

    report.append("## High Priority Events")
    report.append("")

    if high_events:

        for event in high_events:

            report.append(
                f"- `{event.get('event_id', '')}` - "
                f"{event.get('region', 'UNKNOWN')} - "
                f"{event['motion_area_value']} area - "
                f"{event['duration_value']:.2f}s"
            )

    else:

        report.append(
            "No high-priority events in the current history."
        )

    report.append("")

    report.append("## Notes")
    report.append("")
    report.append(
        "Priority is currently a simple heuristic "
        "based on motion area and duration. It does "
        "not mean that Sentinel has identified an "
        "intruder or dangerous activity."
    )
    report.append("")

    report.append(
        "The rules are deliberately simple so they "
        "can be tested and changed as more real "
        "camera data becomes available."
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

    return priority_counts


def main():

    events = load_events()

    if not events:
        print("No event records available.")
        return

    priority_counts = build_report(events)

    print(
        f"Loaded {len(events)} events."
    )

    print(
        f"HIGH: "
        f"{priority_counts['HIGH']}"
    )

    print(
        f"MEDIUM: "
        f"{priority_counts['MEDIUM']}"
    )

    print(
        f"LOW: "
        f"{priority_counts['LOW']}"
    )

    print(
        f"Report saved: {REPORT_FILE}"
    )


if __name__ == "__main__":
    main()