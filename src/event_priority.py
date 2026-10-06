import csv
import os


EVENTS_FILE = "data/events.csv"
REPORT_FILE = "reports/event-priority.md"

# ------------------------------------------------------------
# Base priority rules
# ------------------------------------------------------------

HIGH_MOTION_AREA = 3000
HIGH_DURATION = 10.0

MEDIUM_MOTION_AREA = 1500
MEDIUM_DURATION = 3.0

# ------------------------------------------------------------
# Person-aware rule
# ------------------------------------------------------------

MULTI_PERSON_COUNT = 2
MULTI_PERSON_CONFIDENCE = 0.80


# ============================================================
# Data loading
# ============================================================

def load_events():
    """
    Load event records from the CSV file.

    Older events created before person detection was added
    are supported safely.
    """
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

            # ------------------------------------------------
            # Motion area
            # ------------------------------------------------

            try:
                row["motion_area_value"] = int(
                    float(
                        row.get("motion_area", 0) or 0
                    )
                )
            except (ValueError, TypeError):
                row["motion_area_value"] = 0

            # ------------------------------------------------
            # Duration
            # ------------------------------------------------

            try:
                row["duration_value"] = float(
                    row.get("duration_seconds", 0) or 0
                )
            except (ValueError, TypeError):
                row["duration_value"] = 0.0

            # ------------------------------------------------
            # Object type
            # ------------------------------------------------

            row["object_type_value"] = (
                row.get("object_type", "") or ""
            ).strip().upper()

            # ------------------------------------------------
            # Object count
            # ------------------------------------------------

            try:
                row["object_count_value"] = int(
                    float(
                        row.get("object_count", 0) or 0
                    )
                )
            except (ValueError, TypeError):
                row["object_count_value"] = 0

            # ------------------------------------------------
            # Detection confidence
            # ------------------------------------------------

            try:
                row["detection_confidence_value"] = float(
                    row.get("detection_confidence", 0) or 0
                )
            except (ValueError, TypeError):
                row["detection_confidence_value"] = 0.0

            events.append(row)

    return events


# ============================================================
# Priority helpers
# ============================================================

def calculate_base_priority(event):
    """
    Calculate priority using the original motion/duration rules.
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


def get_base_priority_reason(event):
    """
    Explain why the base priority was assigned.
    """
    motion_area = event["motion_area_value"]
    duration = event["duration_value"]

    if (
        motion_area >= HIGH_MOTION_AREA
        and duration >= HIGH_DURATION
    ):
        return "Large motion area + long duration"

    if motion_area >= HIGH_MOTION_AREA:
        return "Large motion area"

    if duration >= HIGH_DURATION:
        return "Long duration"

    if (
        motion_area >= MEDIUM_MOTION_AREA
        and duration >= MEDIUM_DURATION
    ):
        return "Moderate motion area + moderate duration"

    if motion_area >= MEDIUM_MOTION_AREA:
        return "Moderate motion area"

    if duration >= MEDIUM_DURATION:
        return "Moderate duration"

    return "Small/short event"


def elevate_priority(priority):
    """
    Increase priority by one level.

    HIGH remains HIGH.
    """
    if priority == "LOW":
        return "MEDIUM"

    if priority == "MEDIUM":
        return "HIGH"

    return "HIGH"


def is_multi_person_event(event):
    """
    Check whether the event qualifies for the multi-person rule.
    """
    return (
        event["object_type_value"] == "PERSON"
        and event["object_count_value"] >= MULTI_PERSON_COUNT
        and event["detection_confidence_value"]
        >= MULTI_PERSON_CONFIDENCE
    )


def calculate_priority(event):
    """
    Calculate final priority.

    The base priority comes from motion area and duration.

    A confidently detected multi-person event can increase the
    priority by one level, unless it is already HIGH.
    """
    base_priority = calculate_base_priority(event)

    if is_multi_person_event(event):
        return elevate_priority(base_priority)

    return base_priority


def get_priority_reason(event):
    """
    Explain the final priority decision.
    """
    base_priority = calculate_base_priority(event)
    base_reason = get_base_priority_reason(event)

    if is_multi_person_event(event):
        object_count = event["object_count_value"]
        confidence = event["detection_confidence_value"]

        if base_priority == "HIGH":
            return (
                f"{base_reason}; multi-person detected "
                f"({object_count} people, confidence "
                f"{confidence:.2f}), already HIGH"
            )

        return (
            f"{base_reason}; escalated for multi-person "
            f"detection ({object_count} people, confidence "
            f"{confidence:.2f})"
        )

    return base_reason


# ============================================================
# Report generation
# ============================================================

def build_report(events):
    """
    Create the event priority report.
    """
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
        reason = get_priority_reason(event)

        event["priority"] = priority
        event["priority_reason"] = reason

        priority_counts[priority] += 1
        priority_events.append(event)

    # Newest events first
    priority_events.reverse()

    high_events = [
        event
        for event in priority_events
        if event["priority"] == "HIGH"
    ]

    multi_person_events = [
        event
        for event in priority_events
        if is_multi_person_event(event)
    ]

    person_events = [
        event
        for event in priority_events
        if event["object_type_value"] == "PERSON"
    ]

    # --------------------------------------------------------
    # Report content
    # --------------------------------------------------------

    report = []

    report.append(
        "# Project Sentinel - Event Priority"
    )

    report.append("")

    report.append(
        "This report applies a simple rule-based priority "
        "to the stored events."
    )

    report.append("")

    report.append(
        "The base priority uses motion area and event "
        "duration. Person-aware events can be escalated "
        "when multiple people are detected with sufficient "
        "confidence."
    )

    report.append("")

    # --------------------------------------------------------
    # Current rules
    # --------------------------------------------------------

    report.append("## Current Rules")
    report.append("")

    report.append(
        f"- HIGH base priority: motion area >= "
        f"{HIGH_MOTION_AREA} or duration >= "
        f"{HIGH_DURATION:.0f}s"
    )

    report.append(
        f"- MEDIUM base priority: motion area >= "
        f"{MEDIUM_MOTION_AREA} or duration >= "
        f"{MEDIUM_DURATION:.0f}s"
    )

    report.append(
        "- LOW base priority: everything else"
    )

    report.append(
        f"- Multi-person escalation: PERSON event with "
        f"{MULTI_PERSON_COUNT}+ people and confidence >= "
        f"{MULTI_PERSON_CONFIDENCE:.2f}"
    )

    report.append(
        "- Multi-person escalation increases priority by "
        "one level, up to HIGH"
    )

    report.append("")

    # --------------------------------------------------------
    # Priority summary
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Person summary
    # --------------------------------------------------------

    report.append("## Person Detection Summary")
    report.append("")

    report.append(
        f"- Person-aware events: {len(person_events)}"
    )

    report.append(
        f"- Multi-person events with confidence >= "
        f"{MULTI_PERSON_CONFIDENCE:.2f}: "
        f"{len(multi_person_events)}"
    )

    report.append("")

    # --------------------------------------------------------
    # Events table
    # --------------------------------------------------------

    report.append("## Events")
    report.append("")

    report.append(
        "| Event ID | Camera | Region | Area | Duration | "
        "Object | Count | Confidence | Priority | Reason |"
    )

    report.append(
        "|---|---|---|---:|---:|---|---:|---:|---|---|"
    )

    for event in priority_events:

        object_type = (
            event["object_type_value"]
            if event["object_type_value"]
            else "UNKNOWN"
        )

        object_count = (
            str(event["object_count_value"])
            if event["object_count_value"] > 0
            else "-"
        )

        confidence = (
            f"{event['detection_confidence_value']:.2f}"
            if event["detection_confidence_value"] > 0
            else "-"
        )

        report.append(
            f"| `{event.get('event_id', '')}` | "
            f"{event.get('camera_id', 'UNKNOWN')} | "
            f"{event.get('region', 'UNKNOWN')} | "
            f"{event['motion_area_value']} | "
            f"{event['duration_value']:.2f}s | "
            f"{object_type} | "
            f"{object_count} | "
            f"{confidence} | "
            f"**{event['priority']}** | "
            f"{event['priority_reason']} |"
        )

    report.append("")

    # --------------------------------------------------------
    # High priority events
    # --------------------------------------------------------

    report.append("## High Priority Events")
    report.append("")

    if high_events:

        for event in high_events:

            object_type = (
                event["object_type_value"]
                if event["object_type_value"]
                else "UNKNOWN"
            )

            object_count = event["object_count_value"]
            confidence = event["detection_confidence_value"]

            report.append(
                f"- `{event.get('event_id', '')}` - "
                f"{event.get('region', 'UNKNOWN')} - "
                f"{event['motion_area_value']} area - "
                f"{event['duration_value']:.2f}s - "
                f"{object_type}"
            )

            report.append(
                f"  - Reason: {event['priority_reason']}"
            )

            if (
                object_type == "PERSON"
                and object_count > 0
            ):
                report.append(
                    f"  - People: {object_count} | "
                    f"Confidence: {confidence:.2f}"
                )

    else:

        report.append(
            "No high-priority events in the current history."
        )

    report.append("")

    # --------------------------------------------------------
    # Multi-person events
    # --------------------------------------------------------

    report.append("## Multi-Person Events")
    report.append("")

    if multi_person_events:

        for event in multi_person_events:

            report.append(
                f"- `{event.get('event_id', '')}` - "
                f"{event.get('region', 'UNKNOWN')} - "
                f"{event['object_count_value']} people - "
                f"confidence "
                f"{event['detection_confidence_value']:.2f} - "
                f"priority **{event['priority']}**"
            )

            report.append(
                f"  - Reason: {event['priority_reason']}"
            )

    else:

        report.append(
            "No multi-person events meeting the current "
            "confidence rule."
        )

    report.append("")

    # --------------------------------------------------------
    # Notes
    # --------------------------------------------------------

    report.append("## Notes")
    report.append("")

    report.append(
        "Priority is currently a simple heuristic. It does "
        "not mean that Sentinel has identified an intruder, "
        "threat, crime, or dangerous activity."
    )

    report.append("")

    report.append(
        "Person count and detection confidence are used only "
        "to escalate confidently detected multi-person events "
        "by one priority level."
    )

    report.append("")

    report.append(
        "When a multi-person event is already HIGH because "
        "of motion area or duration, the multi-person rule "
        "does not increase it further. The report records "
        "this explicitly in the priority reason."
    )

    report.append("")

    report.append(
        "Historical events created before person detection "
        "was added are still included in the report. Their "
        "person-related fields remain empty and therefore do "
        "not receive person-aware escalation."
    )

    report.append("")

    report.append(
        "The rules are deliberately simple so they can be "
        "tested and changed as more real camera data becomes "
        "available."
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


# ============================================================
# Main
# ============================================================

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
        f"HIGH: {priority_counts['HIGH']}"
    )

    print(
        f"MEDIUM: {priority_counts['MEDIUM']}"
    )

    print(
        f"LOW: {priority_counts['LOW']}"
    )

    print(
        f"Report saved: {REPORT_FILE}"
    )


if __name__ == "__main__":
    main()