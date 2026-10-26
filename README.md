# Project Sentinel

## Overview

Project Sentinel is an AI-assisted CCTV monitoring project designed to add useful event detection and monitoring capabilities to existing surveillance systems.

The goal is to build a practical, affordable, offline-first solution that can help small businesses understand activity captured by their cameras.

## Project Goals

- Detect people and identify relevant activity.
- Record events with timestamps and camera identifiers.
- Preserve evidence snapshots for recorded events.
- Maintain an event history for review.
- Provide a local dashboard for monitoring and analysis.
- Explore configurable detection zones and smart alerts.
- Keep processing local where practical, reducing dependence on cloud services.

## Current Implementation

The project currently includes:

- Person-detection components.
- Event generation and lifecycle handling.
- Timestamped event history stored in CSV format.
- Evidence snapshot generation.
- Event priority and summary utilities.
- A local web dashboard with event history.
- A live event monitor that handles stale or inactive event status.

The system is still under development. Features and performance will be validated as implementation progresses.

## Hardware

Available CCTV equipment:

- 2 × Hikvision DS-2CE16C0T-IR cameras.
- 2 × Hikvision DS-2CE16D1T-IT3 cameras.
- Tenda S108 network switch.

Full integration with the available analogue CCTV equipment remains part of the development work.

## Project Structure

```text
docs/       Development notes and documentation
src/        Python source code
data/       Event history and locally generated evidence
models/     AI models
reports/    Generated reports and analysis
```

## Running the Dashboard

Activate the project's Python virtual environment, then run:

```powershell
py src\dashboard_server.py
```

Open the following address in your browser:

`http://127.0.0.1:8000`

The dashboard runs locally on the development machine. Detection and monitoring behavior depends on the project's current implementation and configuration.

## Development Approach

The project follows this workflow:

**Build → Test → Observe → Improve → Document → Commit → Push**

Development notes record actual implementation work, test results, limitations, and lessons learned.

## Development Target

**Project Sentinel v1.0 target: 29 November 2026**

This is an active personal engineering project focused on practical CCTV monitoring, software development, and building a demonstrable portfolio project.