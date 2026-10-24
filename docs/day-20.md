# Day 20 - Handling Stale Active Events

Date: 24 October 2026

## What I worked on

Today I continued improving the Live Event Monitor. On Day 19, I got the dashboard to display active person events and return to the inactive state when an event ended.

This time, I worked on another problem: what happens if Sentinel stops unexpectedly while an event is still marked as active?

The active-event information is stored in `data/active_event.json`. If Sentinel stops before clearing that information, the dashboard could display an old event as if it were still active.

I updated `src/dashboard_server.py` to check the `updated_at` timestamp before displaying an active event. The dashboard now ignores active status when the timestamp is more than 10 seconds old, more than 5 seconds in the future, or missing or invalid.

## Testing

First, I checked that both Python files compiled without errors:

    py -m py_compile src\dashboard_server.py src\sentinel.py

The command completed without errors.

I then opened the dashboard with Sentinel stopped. It displayed the message that no active event was currently reported.

## Testing a live event

I started Sentinel and tested person detection again.

The dashboard displayed this event:

- Event ID: EVT-20261024-114915-544292
- Camera: CAM-01
- Primary region: TOP LEFT
- Maximum people detected: 1
- Maximum detection confidence: 0.93
- Latest motion area: 8924 pixels
- Elapsed time observed: 50.4 seconds

The dashboard also displayed the event start time, last status update, and evidence snapshot link.

After the event ended, the dashboard returned to the inactive message.

## Testing stale status

I created a test active-event record with an old timestamp. Although the record indicated that an event was active, the dashboard displayed that no active event was currently reported.

This confirmed that the new timestamp check rejected the outdated status during the test.

The temporary active-event test state was then removed.

## Small issue found

The full `git diff --check` reported trailing whitespace on five lines in the regenerated `reports/event-dashboard.html`.

I checked the intended source change separately, and the whitespace check for `src/dashboard_server.py` passed. I kept the generated dashboard report out of the staged changes because it contained unrelated runtime updates.

## What I learned

The dashboard cannot rely only on the status value in the JSON file. It also needs to check when that information was last updated.

This change helps prevent an old event from being displayed as active after Sentinel stops updating its status. However, it does not delete stale information automatically, and the check depends on the computer's system clock.

The tests were performed manually. More testing, including automated tests and unexpected-shutdown scenarios, would help check the behaviour more thoroughly.

The event history, generated dashboard report, and evidence images from testing are being kept separate from the intended code commit.