# Day 19 - Live Event Monitor

Date: 11 October 2026

## What I worked on

Today I connected the Sentinel detection system to the local dashboard. The goal was to see person events while they are active and confirm that the dashboard updates when an event ends.

I updated `src/sentinel.py` to publish active-event information and `src/dashboard_server.py` to read that information and add the Live Event Monitor to the dashboard response. The generated HTML report remains separate from the live panel.

## Testing

First, I checked the Python files:

    python -m py_compile src\sentinel.py src\dashboard_server.py

The command completed without errors and returned exit code 0.

I then started the dashboard server and opened it in my browser. The dashboard loaded and initially showed that no active person event was being reported.

## Testing a live event

I started Sentinel separately and tested the system with the available camera setup.

The dashboard displayed this event:

- Event ID: EVT-20261011-195033-914290
- Camera: CAM-01
- Primary region: TOP RIGHT
- Maximum people detected: 1
- Maximum detection confidence: 0.95
- Latest motion area: 4151 pixels
- Elapsed time observed: 25 seconds

The dashboard also provided a link to the evidence snapshot.

## What happened when the event ended?

The Sentinel terminal reported that the event had ended. The dashboard then returned to the inactive message.

I checked the event history and confirmed that the completed event was still available. I also opened the evidence snapshot successfully.

This confirmed that the live panel could display an active event and return to its inactive state without losing the completed event record.

## Small issue fixed

The first `git diff --check` reported trailing whitespace on five lines in the generated dashboard HTML. I removed the extra spaces and ran the check again. It then returned no errors.

## What I learned

Displaying a live event is only part of the job. I also needed to check what happened after the event ended and make sure its history and evidence were preserved.

The local integration test passed, although further testing would be needed to cover other situations and possible failures.

The event history and evidence files generated during testing are being kept separate from the code commit.
