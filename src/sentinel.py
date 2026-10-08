import csv
import os
from collections import Counter
from datetime import datetime

import cv2
import numpy as np


# ============================================================
# Project Sentinel - Integrated Motion + Person Detection
# ============================================================

CAMERA_ID = "CAM-01"

MODEL_PATH = "models/yolo26n.onnx"
EVENT_FILE = "data/events.csv"
EVIDENCE_DIR = "data/evidence"

# Camera / display
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Motion detection
MOTION_PERCENT_THRESHOLD = 3.0
MOTION_CONFIRM_FRAMES = 2
NO_CHANGE_FRAMES_TO_END = 30

# YOLO
PERSON_CLASS_ID = 0
PERSON_CONFIDENCE_THRESHOLD = 0.65
NMS_THRESHOLD = 0.55

# Event history format
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
    "object_type",
    "object_count",
    "detection_confidence",
    "duration_seconds",
]


# ============================================================
# Utility functions
# ============================================================

def generate_event_id():
    """
    Generate a unique event ID.
    """
    now = datetime.now()

    return now.strftime(
        "EVT-%Y%m%d-%H%M%S-%f"
    )


def prepare_event_file():
    """
    Make sure the event CSV exists and uses the current schema.

    Older Sentinel event records are preserved.
    """
    os.makedirs(
        os.path.dirname(EVENT_FILE),
        exist_ok=True
    )

    if not os.path.exists(EVENT_FILE):

        with open(
            EVENT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=EVENT_FIELDS
            )

            writer.writeheader()

        print(
            "Created person-aware event history."
        )

        return

    with open(
        EVENT_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        old_fields = reader.fieldnames or []
        old_rows = list(reader)

    if old_fields == EVENT_FIELDS:
        return

    print(
        "Updating event history for person-aware events..."
    )

    updated_rows = []

    for row in old_rows:

        updated_row = {
            field: ""
            for field in EVENT_FIELDS
        }

        for field in EVENT_FIELDS:

            if field in row:
                updated_row[field] = (
                    row.get(field, "")
                )

        updated_rows.append(
            updated_row
        )

    with open(
        EVENT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=EVENT_FIELDS
        )

        writer.writeheader()
        writer.writerows(updated_rows)

    print(
        f"Event history updated. "
        f"{len(updated_rows)} existing events kept."
    )


def save_event(event):
    """
    Save one completed event to the CSV history.
    """
    with open(
        EVENT_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=EVENT_FIELDS
        )

        writer.writerow(event)


# ============================================================
# YOLO helper functions
# ============================================================

def letterbox(image, new_shape=(640, 640)):
    """
    Resize an image while keeping its aspect ratio.

    Returns:
        resized_image, scale, pad_x, pad_y
    """
    original_height, original_width = image.shape[:2]

    target_width, target_height = new_shape

    scale = min(
        target_width / original_width,
        target_height / original_height
    )

    resized_width = int(
        round(original_width * scale)
    )

    resized_height = int(
        round(original_height * scale)
    )

    resized = cv2.resize(
        image,
        (resized_width, resized_height),
        interpolation=cv2.INTER_LINEAR
    )

    pad_x = target_width - resized_width
    pad_y = target_height - resized_height

    left = pad_x // 2
    right = pad_x - left

    top = pad_y // 2
    bottom = pad_y - top

    resized = cv2.copyMakeBorder(
        resized,
        top,
        bottom,
        left,
        right,
        cv2.BORDER_CONSTANT,
        value=(114, 114, 114)
    )

    return (
        resized,
        scale,
        left,
        top
    )


def convert_box_to_original(
    x1,
    y1,
    x2,
    y2,
    scale,
    pad_x,
    pad_y,
    original_width,
    original_height,
):
    """
    Convert YOLO letterboxed coordinates back to the
    original camera frame.
    """
    x1 = (x1 - pad_x) / scale
    y1 = (y1 - pad_y) / scale

    x2 = (x2 - pad_x) / scale
    y2 = (y2 - pad_y) / scale

    x1 = max(
        0,
        min(
            int(round(x1)),
            original_width - 1
        )
    )

    y1 = max(
        0,
        min(
            int(round(y1)),
            original_height - 1
        )
    )

    x2 = max(
        0,
        min(
            int(round(x2)),
            original_width - 1
        )
    )

    y2 = max(
        0,
        min(
            int(round(y2)),
            original_height - 1
        )
    )

    return (
        x1,
        y1,
        x2,
        y2
    )


def detect_persons(frame, model):
    """
    Run YOLO person detection.

    Supports the YOLO ONNX formats already used by
    Project Sentinel:

        (1, 300, 6)
        (1, 84, 8400)

    Returns a list of person detections.
    """
    original_height, original_width = frame.shape[:2]

    input_size = (640, 640)

    image, scale, pad_x, pad_y = letterbox(
        frame,
        input_size
    )

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    blob = cv2.dnn.blobFromImage(
        image,
        scalefactor=1 / 255.0,
        size=input_size,
        swapRB=False,
        crop=False
    )

    model.setInput(blob)

    outputs = model.forward()

    output = outputs

    if isinstance(
        outputs,
        (list, tuple)
    ):
        output = outputs[0]

    output = np.array(output)

    detections = []

    # --------------------------------------------------------
    # Format A:
    # (1, 300, 6)
    #
    # [x1, y1, x2, y2, score, class_id]
    # --------------------------------------------------------

    if (
        output.ndim == 3
        and output.shape[-1] == 6
    ):

        rows = output[0]

        for row in rows:

            (
                x1,
                y1,
                x2,
                y2,
                confidence,
                class_id
            ) = row

            confidence = float(
                confidence
            )

            class_id = int(
                class_id
            )

            if (
                confidence
                < PERSON_CONFIDENCE_THRESHOLD
            ):
                continue

            if class_id != PERSON_CLASS_ID:
                continue

            (
                x1,
                y1,
                x2,
                y2
            ) = convert_box_to_original(
                x1,
                y1,
                x2,
                y2,
                scale,
                pad_x,
                pad_y,
                original_width,
                original_height,
            )

            width = max(
                0,
                x2 - x1
            )

            height = max(
                0,
                y2 - y1
            )

            if (
                width <= 0
                or height <= 0
            ):
                continue

            detections.append(
                {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "confidence": confidence,
                }
            )

    # --------------------------------------------------------
    # Format B:
    # (1, 84, 8400)
    #
    # Standard YOLO raw output:
    # 4 box values + 80 class scores
    # --------------------------------------------------------

    elif (
        output.ndim == 3
        and output.shape[1] == 84
    ):

        predictions = output[0].T

        boxes = []
        confidences = []

        for prediction in predictions:

            center_x = float(
                prediction[0]
            )

            center_y = float(
                prediction[1]
            )

            width = float(
                prediction[2]
            )

            height = float(
                prediction[3]
            )

            class_scores = prediction[4:]

            class_id = int(
                np.argmax(class_scores)
            )

            confidence = float(
                class_scores[class_id]
            )

            if class_id != PERSON_CLASS_ID:
                continue

            if (
                confidence
                < PERSON_CONFIDENCE_THRESHOLD
            ):
                continue

            x1 = (
                center_x
                - width / 2
            )

            y1 = (
                center_y
                - height / 2
            )

            x2 = (
                center_x
                + width / 2
            )

            y2 = (
                center_y
                + height / 2
            )

            (
                x1,
                y1,
                x2,
                y2
            ) = convert_box_to_original(
                x1,
                y1,
                x2,
                y2,
                scale,
                pad_x,
                pad_y,
                original_width,
                original_height,
            )

            box_width = max(
                0,
                x2 - x1
            )

            box_height = max(
                0,
                y2 - y1
            )

            if (
                box_width <= 0
                or box_height <= 0
            ):
                continue

            boxes.append(
                [
                    x1,
                    y1,
                    box_width,
                    box_height,
                ]
            )

            confidences.append(
                confidence
            )

        if boxes:

            indices = cv2.dnn.NMSBoxes(
                boxes,
                confidences,
                PERSON_CONFIDENCE_THRESHOLD,
                NMS_THRESHOLD
            )

            if len(indices) > 0:

                for index in np.array(
                    indices
                ).flatten():

                    x, y, width, height = (
                        boxes[index]
                    )

                    detections.append(
                        {
                            "x1": int(x),
                            "y1": int(y),
                            "x2": int(
                                x + width
                            ),
                            "y2": int(
                                y + height
                            ),
                            "confidence": float(
                                confidences[index]
                            ),
                        }
                    )

    return detections


# ============================================================
# Motion detection
# ============================================================

def detect_motion(
    previous_gray,
    current_gray
):
    """
    Detect motion and determine the strongest region.

    Returns None when there is no useful motion.
    """
    frame_height, frame_width = (
        current_gray.shape
    )

    difference = cv2.absdiff(
        previous_gray,
        current_gray
    )

    _, threshold = cv2.threshold(
        difference,
        25,
        255,
        cv2.THRESH_BINARY
    )

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    threshold = cv2.morphologyEx(
        threshold,
        cv2.MORPH_CLOSE,
        kernel
    )

    threshold = cv2.dilate(
        threshold,
        kernel,
        iterations=2
    )

    # --------------------------------------------------------
    # Find largest useful motion contour
    # --------------------------------------------------------

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    largest_area = 0
    largest_bbox = None

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area <= largest_area:
            continue

        x, y, width, height = (
            cv2.boundingRect(contour)
        )

        if (
            width < 10
            or height < 10
        ):
            continue

        largest_area = area

        largest_bbox = (
            x,
            y,
            width,
            height
        )

    # --------------------------------------------------------
    # Regional motion percentage
    # --------------------------------------------------------

    h_mid = frame_height // 2
    w_mid = frame_width // 2

    regions = {
        "TOP LEFT": threshold[
            0:h_mid,
            0:w_mid
        ],

        "TOP RIGHT": threshold[
            0:h_mid,
            w_mid:frame_width
        ],

        "BOTTOM LEFT": threshold[
            h_mid:frame_height,
            0:w_mid
        ],

        "BOTTOM RIGHT": threshold[
            h_mid:frame_height,
            w_mid:frame_width
        ],
    }

    best_region = None
    best_motion_percent = 0.0

    for (
        region_name,
        region_image
    ) in regions.items():

        changed_pixels = (
            cv2.countNonZero(
                region_image
            )
        )

        total_pixels = (
            region_image.shape[0]
            * region_image.shape[1]
        )

        motion_percent = (
            changed_pixels
            / total_pixels
        ) * 100

        if (
            motion_percent
            > best_motion_percent
        ):

            best_motion_percent = (
                motion_percent
            )

            best_region = (
                region_name
            )

    if best_region is None:
        return None

    if (
        best_motion_percent
        < MOTION_PERCENT_THRESHOLD
    ):
        return None

    if largest_bbox is None:
        return None

    x, y, width, height = (
        largest_bbox
    )

    return {
        "region": best_region,
        "motion_percent": (
            best_motion_percent
        ),
        "motion_area": int(
            largest_area
        ),
        "bbox_x": int(x),
        "bbox_y": int(y),
        "bbox_width": int(width),
        "bbox_height": int(height),
    }


# ============================================================
# Event handling
# ============================================================

def get_dominant_region(region_counts):
    """
    Return the region seen most often during the event.

    Counter.most_common() preserves the first-seen region when
    two regions have the same count, making the result stable.
    """
    if not region_counts:
        return "UNKNOWN"

    return region_counts.most_common(1)[0][0]


def create_event_record(
    event_id,
    start_time,
    end_time,
    motion_data,
    dominant_region,
    max_person_count,
    max_detection_confidence,
    evidence_path,
):
    """
    Build a completed event record.

    The stored region is the dominant region observed during
    the event rather than simply the region seen on the final
    frame.
    """
    duration = (
        end_time - start_time
    ).total_seconds()

    return {
        "event_id": event_id,
        "camera_id": CAMERA_ID,
        "start_time": start_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "end_time": end_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "region": dominant_region,
        "motion_area": motion_data[
            "motion_area"
        ],
        "bbox_x": motion_data[
            "bbox_x"
        ],
        "bbox_y": motion_data[
            "bbox_y"
        ],
        "bbox_width": motion_data[
            "bbox_width"
        ],
        "bbox_height": motion_data[
            "bbox_height"
        ],
        "evidence_path": evidence_path,
        "object_type": "PERSON",
        "object_count": max_person_count,
        "detection_confidence": (
            f"{max_detection_confidence:.2f}"
        ),
        "duration_seconds": (
            f"{duration:.2f}"
        ),
    }


def save_evidence(
    frame,
    event_id
):
    """
    Save one evidence image.

    The filesystem uses the normal Windows path internally,
    while the stored CSV path always uses forward slashes.
    """
    os.makedirs(
        EVIDENCE_DIR,
        exist_ok=True
    )

    filename = (
        f"{event_id}.jpg"
    )

    filesystem_path = os.path.join(
        EVIDENCE_DIR,
        filename
    )

    cv2.imwrite(
        filesystem_path,
        frame
    )

    csv_path = filesystem_path.replace(
        "\\",
        "/"
    )

    print(
        f"Evidence saved: {csv_path}"
    )

    return csv_path


# ============================================================
# Main
# ============================================================

def main():

    prepare_event_file()

    if not os.path.exists(
        MODEL_PATH
    ):

        print(
            f"ERROR: YOLO model not found: "
            f"{MODEL_PATH}"
        )

        return

    print(
        "Loading YOLO model..."
    )

    model = cv2.dnn.readNetFromONNX(
        MODEL_PATH
    )

    print(
        "YOLO model loaded."
    )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print(
            "ERROR: Could not open camera."
        )

        return

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        FRAME_WIDTH
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        FRAME_HEIGHT
    )

    previous_gray = None

    # --------------------------------------------------------
    # Event state
    # --------------------------------------------------------

    event_active = False

    event_id = None

    event_start_time = None

    event_evidence_path = ""

    current_motion = None

    # Track regions seen throughout the active event.
    event_region_counts = Counter()

    max_person_count = 0

    max_detection_confidence = 0.0

    motion_confirmation_counter = 0

    no_change_counter = 0

    try:

        while True:

            success, frame = camera.read()

            if not success:

                print(
                    "ERROR: Could not read frame."
                )

                break

            frame = cv2.resize(
                frame,
                (
                    FRAME_WIDTH,
                    FRAME_HEIGHT
                )
            )

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            # ------------------------------------------------
            # Initialize previous frame
            # ------------------------------------------------

            if previous_gray is None:

                previous_gray = gray

                continue

            # ------------------------------------------------
            # Motion
            # ------------------------------------------------

            motion = detect_motion(
                previous_gray,
                gray
            )

            # ------------------------------------------------
            # Person detection
            # ------------------------------------------------

            person_detections = (
                detect_persons(
                    frame,
                    model
                )
            )

            person_count = len(
                person_detections
            )

            current_confidence = 0.0

            if person_detections:

                current_confidence = max(
                    detection[
                        "confidence"
                    ]
                    for detection
                    in person_detections
                )

            # ------------------------------------------------
            # Draw person boxes
            # ------------------------------------------------

            for detection in (
                person_detections
            ):

                x1 = detection["x1"]
                y1 = detection["y1"]
                x2 = detection["x2"]
                y2 = detection["y2"]

                confidence = (
                    detection[
                        "confidence"
                    ]
                )

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                label = (
                    f"PERSON "
                    f"{confidence:.2f}"
                )

                cv2.putText(
                    frame,
                    label,
                    (
                        x1,
                        max(
                            20,
                            y1 - 8
                        )
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
                    2
                )

            # ------------------------------------------------
            # Draw motion bounding box
            # ------------------------------------------------

            if motion is not None:

                x = motion["bbox_x"]
                y = motion["bbox_y"]

                width = (
                    motion[
                        "bbox_width"
                    ]
                )

                height = (
                    motion[
                        "bbox_height"
                    ]
                )

                cv2.rectangle(
                    frame,
                    (x, y),
                    (
                        x + width,
                        y + height
                    ),
                    (255, 0, 0),
                    2
                )

                motion_label = (
                    f"{motion['region']} "
                    f"{motion['motion_percent']:.2f}%"
                )

                cv2.putText(
                    frame,
                    motion_label,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2
                )

            # ------------------------------------------------
            # Determine whether current frame qualifies
            # ------------------------------------------------

            valid_detection = (
                motion is not None
                and person_count > 0
            )

            if valid_detection:

                motion_confirmation_counter += 1

                no_change_counter = 0

                if (
                    motion_confirmation_counter
                    >= MOTION_CONFIRM_FRAMES
                ):

                    # ----------------------------------------
                    # Start event
                    # ----------------------------------------

                    if not event_active:

                        event_active = True

                        event_id = (
                            generate_event_id()
                        )

                        event_start_time = (
                            datetime.now()
                        )

                        event_evidence_path = (
                            save_evidence(
                                frame,
                                event_id
                            )
                        )

                        max_person_count = (
                            person_count
                        )

                        max_detection_confidence = (
                            current_confidence
                        )

                        current_motion = (
                            motion.copy()
                        )

                        # Start tracking event regions.
                        event_region_counts = Counter()

                        event_region_counts[
                            motion["region"]
                        ] += 1

                        print(
                            f"PERSON EVENT STARTED! "
                            f"ID: {event_id} | "
                            f"Camera: {CAMERA_ID} | "
                            f"Region: {motion['region']} | "
                            f"People at start: "
                            f"{person_count} | "
                            f"Confidence: "
                            f"{current_confidence:.2f}"
                        )

                    # ----------------------------------------
                    # Continue existing event
                    # ----------------------------------------

                    else:

                        # Track every region observed during
                        # the active event.
                        event_region_counts[
                            motion["region"]
                        ] += 1

                        if (
                            person_count
                            > max_person_count
                        ):

                            max_person_count = (
                                person_count
                            )

                        if (
                            current_confidence
                            > max_detection_confidence
                        ):

                            max_detection_confidence = (
                                current_confidence
                            )

                        current_motion = (
                            motion.copy()
                        )

            else:

                motion_confirmation_counter = 0

                if event_active:

                    no_change_counter += 1

                    # ----------------------------------------
                    # End event
                    # ----------------------------------------

                    if (
                        no_change_counter
                        >= NO_CHANGE_FRAMES_TO_END
                    ):

                        event_end_time = (
                            datetime.now()
                        )

                        dominant_region = (
                            get_dominant_region(
                                event_region_counts
                            )
                        )

                        event = create_event_record(
                            event_id=event_id,
                            start_time=(
                                event_start_time
                            ),
                            end_time=(
                                event_end_time
                            ),
                            motion_data=current_motion,
                            dominant_region=(
                                dominant_region
                            ),
                            max_person_count=(
                                max_person_count
                            ),
                            max_detection_confidence=(
                                max_detection_confidence
                            ),
                            evidence_path=(
                                event_evidence_path
                            ),
                        )

                        save_event(
                            event
                        )

                        duration = (
                            event_end_time
                            - event_start_time
                        ).total_seconds()

                        print(
                            f"PERSON EVENT ENDED | "
                            f"ID: {event_id} | "
                            f"Primary Region: "
                            f"{dominant_region} | "
                            f"Duration: "
                            f"{duration:.2f}s | "
                            f"Max People: "
                            f"{max_person_count} | "
                            f"Max Confidence: "
                            f"{max_detection_confidence:.2f}"
                        )

                        # Reset event state
                        event_active = False

                        event_id = None

                        event_start_time = None

                        event_evidence_path = ""

                        current_motion = None

                        event_region_counts = Counter()

                        max_person_count = 0

                        max_detection_confidence = 0.0

                        no_change_counter = 0

            # ------------------------------------------------
            # Display information
            # ------------------------------------------------

            status = (
                "EVENT ACTIVE"
                if event_active
                else "MONITORING"
            )

            cv2.putText(
                frame,
                f"Sentinel | "
                f"{CAMERA_ID} | "
                f"{status}",
                (
                    10,
                    FRAME_HEIGHT - 40
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"People detected: "
                f"{person_count}",
                (
                    10,
                    FRAME_HEIGHT - 15
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.60,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Project Sentinel",
                frame
            )

            previous_gray = gray

            # ------------------------------------------------
            # Quit
            # ------------------------------------------------

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):
                break

    except KeyboardInterrupt:

        print(
            "\nStopping Sentinel..."
        )

    finally:

        # ----------------------------------------------------
        # Finalize active event on exit
        # ----------------------------------------------------

        if (
            event_active
            and event_start_time is not None
            and current_motion is not None
        ):

            event_end_time = (
                datetime.now()
            )

            dominant_region = (
                get_dominant_region(
                    event_region_counts
                )
            )

            event = create_event_record(
                event_id=event_id,
                start_time=event_start_time,
                end_time=event_end_time,
                motion_data=current_motion,
                dominant_region=dominant_region,
                max_person_count=max_person_count,
                max_detection_confidence=(
                    max_detection_confidence
                ),
                evidence_path=event_evidence_path,
            )

            save_event(
                event
            )

            duration = (
                event_end_time
                - event_start_time
            ).total_seconds()

            print(
                f"PERSON EVENT FINALIZED ON EXIT | "
                f"ID: {event_id} | "
                f"Primary Region: "
                f"{dominant_region} | "
                f"Duration: "
                f"{duration:.2f}s | "
                f"Max People: "
                f"{max_person_count} | "
                f"Max Confidence: "
                f"{max_detection_confidence:.2f}"
            )

        camera.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()