import cv2
import csv
import os
from datetime import datetime

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Could not open camera.")
    exit()

previous_frame = None

# Ignore very small motion areas
MIN_CONTOUR_AREA = 800

# Number of consecutive frames needed to confirm an event
START_CONFIRM_FRAMES = 2

# Quiet frames needed to end an event
NO_CHANGE_FRAMES_TO_END = 30

# Event history file
EVENTS_FILE = "data/events.csv"

# Create the data folder if it does not already exist
os.makedirs("data", exist_ok=True)

# Create the CSV file with headings the first time it is used
if not os.path.exists(EVENTS_FILE):
    with open(EVENTS_FILE, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "event_id",
            "start_time",
            "end_time",
            "region",
            "motion_area",
            "duration_seconds"
        ])

event_active = False
no_change_frames = 0

candidate_region = None
start_confirm_frames = 0

event_id = None
event_start_time = None
event_region = None
event_area = None

while True:

    success, frame = camera.read()

    if not success:
        print("Could not read frame.")
        break

    height, width = frame.shape[:2]

    # Find the centre of the camera image
    mid_x = width // 2
    mid_y = height // 2

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

            # Motion exists, so reset the quiet-frame counter
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

                    # Create a unique event ID
                    event_id = (
                        "EVT-"
                        + datetime.now().strftime(
                            "%Y%m%d-%H%M%S-%f"
                        )
                    )

                    # Save event information
                    event_start_time = datetime.now()
                    event_region = active_region
                    event_area = largest_area

                    print(
                        f"EVENT STARTED! "
                        f"ID: {event_id} | "
                        f"Region: {event_region} | "
                        f"Area: {event_area:.0f}"
                    )

            # Draw bounding box around detected motion
            cv2.rectangle(
                frame,
                (x, y),
                (x + box_width, y + box_height),
                (255, 255, 255),
                2
            )

            # Display current motion information
            cv2.putText(
                frame,
                f"Motion: {active_region}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Area: {largest_area:.0f}",
                (10, 60),
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

                    # Save the completed event
                    with open(
                        EVENTS_FILE,
                        "a",
                        newline=""
                    ) as file:

                        writer = csv.writer(file)

                        writer.writerow([
                            event_id,
                            event_start_time.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            event_end_time.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            event_region,
                            int(event_area),
                            f"{duration:.2f}"
                        ])

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

    # Draw the four region boundaries
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

    # Save current frame for the next comparison
    previous_frame = gray_frame

    cv2.imshow(
        "Project Sentinel - Event History",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()