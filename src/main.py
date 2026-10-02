import cv2
import csv
import os
from datetime import datetime

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Could not open camera.")
    exit()

previous_frame = None

# Camera identity
CAMERA_ID = "CAM-01"

# Ignore very small motion areas
MIN_CONTOUR_AREA = 800

# Number of consecutive frames needed to confirm an event
START_CONFIRM_FRAMES = 2

# Quiet frames needed to end an event
NO_CHANGE_FRAMES_TO_END = 30

# Event history file
EVENTS_FILE = "data/events.csv"

# Folder for event evidence images
EVIDENCE_DIR = "data/evidence"

# Current event fields
EVENT_FIELDS = [
    "event_id",
    "camera_id",
    "start_time",
    "end_time",
    "region",
    "motion_area",
    "bbox_x",
    "bbox_y",
    "bbox_width",
    "bbox_height",
    "evidence_path",
    "duration_seconds"
]

# Create required folders
os.makedirs("data", exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)


def prepare_event_file():
    """
    Create the event file or upgrade the older Day 8/Day 9 format.
    """

    if not os.path.exists(EVENTS_FILE):

        with open(
            EVENTS_FILE,
            "w",
            newline=""
        ) as file:

            writer = csv.writer(file)
            writer.writerow(EVENT_FIELDS)

        return

    # Read existing event history
    with open(
        EVENTS_FILE,
        "r",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        old_fields = reader.fieldnames
        rows = list(reader)

    # No migration needed if already using the new format
    if old_fields == EVENT_FIELDS:
        return

    print("Updating existing event history format...")

    migrated_rows = []

    for row in rows:

        event_id = row.get("event_id", "")

        evidence_file = os.path.join(
            EVIDENCE_DIR,
            event_id + ".jpg"
        )

        if os.path.exists(evidence_file):
            evidence_path = (
                "data/evidence/"
                + event_id
                + ".jpg"
            )
        else:
            evidence_path = ""

        migrated_rows.append({
            "event_id": event_id,
            "camera_id": CAMERA_ID,
            "start_time": row.get(
                "start_time",
                ""
            ),
            "end_time": row.get(
                "end_time",
                ""
            ),
            "region": row.get(
                "region",
                ""
            ),
            "motion_area": row.get(
                "motion_area",
                ""
            ),
            "bbox_x": "",
            "bbox_y": "",
            "bbox_width": "",
            "bbox_height": "",
            "evidence_path": evidence_path,
            "duration_seconds": row.get(
                "duration_seconds",
                ""
            )
        })

    # Rewrite file using the new format
    with open(
        EVENTS_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=EVENT_FIELDS
        )

        writer.writeheader()
        writer.writerows(migrated_rows)

    print(
        f"Event history updated. "
        f"{len(migrated_rows)} existing events kept."
    )


prepare_event_file()

event_active = False
no_change_frames = 0

candidate_region = None
start_confirm_frames = 0

event_id = None
event_start_time = None
event_region = None
event_area = None
event_bbox = None
event_evidence_path = None


while True:

    success, frame = camera.read()

    if not success:
        print("Could not read frame.")
        break

    height, width = frame.shape[:2]

    # Find the centre of the camera image
    mid_x = width // 2
    mid_y = height // 2

    # Keep a copy of the original camera frame
    original_frame = frame.copy()

    # Convert current frame to grayscale
    gray_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    # Reduce small camera noise
    gray_frame = cv2.GaussianBlur(
        gray_frame,
        (5, 5),
        0
    )

    if previous_frame is not None:

        # Compare current frame with previous frame
        difference = cv2.absdiff(
            previous_frame,
            gray_frame
        )

        # Ignore very small pixel differences
        _, motion_mask = cv2.threshold(
            difference,
            25,
            255,
            cv2.THRESH_BINARY
        )

        # Remove small isolated noise
        small_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (3, 3)
        )

        motion_mask = cv2.morphologyEx(
            motion_mask,
            cv2.MORPH_OPEN,
            small_kernel
        )

        # Join nearby motion areas
        merge_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (7, 7)
        )

        motion_mask = cv2.morphologyEx(
            motion_mask,
            cv2.MORPH_CLOSE,
            merge_kernel
        )

        motion_mask = cv2.dilate(
            motion_mask,
            merge_kernel,
            iterations=1
        )

        # Find motion areas
        contours, _ = cv2.findContours(
            motion_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        largest_area = 0
        largest_box = None

        # Find the largest useful motion area
        for contour in contours:

            area = cv2.contourArea(contour)

            if area >= MIN_CONTOUR_AREA and area > largest_area:

                largest_area = area
                largest_box = cv2.boundingRect(contour)

        if largest_box is not None:

            x, y, box_width, box_height = largest_box

            # Find the centre of the detected motion
            center_x = x + (box_width // 2)
            center_y = y + (box_height // 2)

            # Determine the approximate region
            if center_x < mid_x and center_y < mid_y:
                active_region = "TOP LEFT"

            elif center_x >= mid_x and center_y < mid_y:
                active_region = "TOP RIGHT"

            elif center_x < mid_x and center_y >= mid_y:
                active_region = "BOTTOM LEFT"

            else:
                active_region = "BOTTOM RIGHT"

            # Motion exists, so reset quiet-frame counter
            no_change_frames = 0

            # Confirm motion before starting an event
            if not event_active:

                if candidate_region == active_region:
                    start_confirm_frames += 1
                else:
                    candidate_region = active_region
                    start_confirm_frames = 1

                if start_confirm_frames >= START_CONFIRM_FRAMES:

                    event_active = True
                    start_confirm_frames = 0
                    candidate_region = None

                    # Create event ID
                    event_id = (
                        "EVT-"
                        + datetime.now().strftime(
                            "%Y%m%d-%H%M%S-%f"
                        )
                    )

                    # Record event information
                    event_start_time = datetime.now()
                    event_region = active_region
                    event_area = largest_area
                    event_bbox = (
                        x,
                        y,
                        box_width,
                        box_height
                    )

                    # Create evidence path
                    evidence_filename = (
                        event_id + ".jpg"
                    )

                    event_evidence_path = os.path.join(
                        EVIDENCE_DIR,
                        evidence_filename
                    )

                    # Save original camera frame
                    saved = cv2.imwrite(
                        event_evidence_path,
                        original_frame
                    )

                    if saved:
                        print(
                            f"Evidence saved: "
                            f"{event_evidence_path}"
                        )
                    else:
                        print(
                            "Could not save event evidence."
                        )

                    print(
                        f"EVENT STARTED! "
                        f"ID: {event_id} | "
                        f"Camera: {CAMERA_ID} | "
                        f"Region: {event_region} | "
                        f"Area: {event_area:.0f}"
                    )

            # Draw the motion box
            cv2.rectangle(
                frame,
                (x, y),
                (x + box_width, y + box_height),
                (255, 255, 255),
                2
            )

            # Display camera ID
            cv2.putText(
                frame,
                f"Camera: {CAMERA_ID}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            # Display region
            cv2.putText(
                frame,
                f"Motion: {active_region}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            # Display motion area
            cv2.putText(
                frame,
                f"Area: {largest_area:.0f}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

        else:

            # No useful motion found
            candidate_region = None
            start_confirm_frames = 0

            if event_active:

                no_change_frames += 1

                if no_change_frames >= NO_CHANGE_FRAMES_TO_END:

                    event_end_time = datetime.now()

                    duration = (
                        event_end_time - event_start_time
                    ).total_seconds()

                    x, y, box_width, box_height = event_bbox

                    # Save completed event
                    with open(
                        EVENTS_FILE,
                        "a",
                        newline=""
                    ) as file:

                        writer = csv.DictWriter(
                            file,
                            fieldnames=EVENT_FIELDS
                        )

                        writer.writerow({
                            "event_id": event_id,
                            "camera_id": CAMERA_ID,
                            "start_time":
                                event_start_time.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                            "end_time":
                                event_end_time.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                            "region": event_region,
                            "motion_area": int(event_area),
                            "bbox_x": x,
                            "bbox_y": y,
                            "bbox_width": box_width,
                            "bbox_height": box_height,
                            "evidence_path":
                                "data/evidence/"
                                + event_id
                                + ".jpg",
                            "duration_seconds":
                                f"{duration:.2f}"
                        })

                    print(
                        f"EVENT ENDED | "
                        f"ID: {event_id} | "
                        f"Duration: {duration:.2f}s"
                    )

                    event_active = False
                    no_change_frames = 0

                    event_id = None
                    event_start_time = None
                    event_region = None
                    event_area = None
                    event_bbox = None
                    event_evidence_path = None

    # Draw region boundaries
    cv2.line(
        frame,
        (mid_x, 0),
        (mid_x, height),
        (255, 255, 255),
        1
    )

    cv2.line(
        frame,
        (0, mid_y),
        (width, mid_y),
        (255, 255, 255),
        1
    )

    # Save current frame for next comparison
    previous_frame = gray_frame

    cv2.imshow(
        "Project Sentinel - Event Metadata",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()