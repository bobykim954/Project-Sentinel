import cv2
import numpy as np


MODEL_PATH = "models/yolo26n.onnx"

PERSON_CLASS_ID = 0

# Only accept stronger person detections.
# Based on our actual tests:
# real people: 0.75 - 0.98
# bag false-positive: 0.43 - 0.58
CONFIDENCE_THRESHOLD = 0.65

# Keep separate nearby people from being merged too aggressively
NMS_THRESHOLD = 0.55

INPUT_WIDTH = 640
INPUT_HEIGHT = 640


def letterbox(image, new_width, new_height):
    """Resize image while keeping its original aspect ratio."""

    original_height, original_width = image.shape[:2]

    scale = min(
        new_width / original_width,
        new_height / original_height
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

    pad_x = (new_width - resized_width) // 2
    pad_y = (new_height - resized_height) // 2

    padded = np.full(
        (new_height, new_width, 3),
        114,
        dtype=np.uint8
    )

    padded[
        pad_y:pad_y + resized_height,
        pad_x:pad_x + resized_width
    ] = resized

    return padded, scale, pad_x, pad_y


def convert_box_to_original(
    x1,
    y1,
    x2,
    y2,
    scale,
    pad_x,
    pad_y,
    frame_width,
    frame_height
):
    """Convert model coordinates back to camera coordinates."""

    x1 = (x1 - pad_x) / scale
    y1 = (y1 - pad_y) / scale

    x2 = (x2 - pad_x) / scale
    y2 = (y2 - pad_y) / scale

    x1 = max(
        0,
        min(int(x1), frame_width - 1)
    )

    y1 = max(
        0,
        min(int(y1), frame_height - 1)
    )

    x2 = max(
        0,
        min(int(x2), frame_width - 1)
    )

    y2 = max(
        0,
        min(int(y2), frame_height - 1)
    )

    return x1, y1, x2, y2


# Load the ONNX model
try:
    net = cv2.dnn.readNetFromONNX(
        MODEL_PATH
    )

except Exception as error:

    print(
        f"Could not load model: {error}"
    )

    exit()


camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print(
        "Could not open camera."
    )

    exit()


person_detected = False


while True:

    success, frame = camera.read()

    if not success:

        print(
            "Could not read frame."
        )

        break

    frame_height, frame_width = frame.shape[:2]

    # Keep the original camera frame for display
    display_frame = frame.copy()

    # Resize while preserving aspect ratio
    input_image, scale, pad_x, pad_y = letterbox(
        frame,
        INPUT_WIDTH,
        INPUT_HEIGHT
    )

    # Prepare image for YOLO
    blob = cv2.dnn.blobFromImage(
        input_image,
        scalefactor=1 / 255.0,
        size=(
            INPUT_WIDTH,
            INPUT_HEIGHT
        ),
        swapRB=True,
        crop=False
    )

    net.setInput(blob)

    output = net.forward()

    persons = []

    # -------------------------------------------------
    # YOLO END-TO-END OUTPUT
    #
    # Expected shape:
    # (1, 300, 6)
    #
    # Values:
    # x1, y1, x2, y2, confidence, class_id
    # -------------------------------------------------

    if (
        output.ndim == 3
        and output.shape[-1] == 6
    ):

        detections = output[0]

        for detection in detections:

            x1, y1, x2, y2, confidence, class_id = (
                detection
            )

            confidence = float(
                confidence
            )

            class_id = int(
                class_id
            )

            # We only want people
            if class_id != PERSON_CLASS_ID:
                continue

            if confidence < CONFIDENCE_THRESHOLD:
                continue

            x1, y1, x2, y2 = (
                convert_box_to_original(
                    x1,
                    y1,
                    x2,
                    y2,
                    scale,
                    pad_x,
                    pad_y,
                    frame_width,
                    frame_height
                )
            )

            persons.append(
                (
                    x1,
                    y1,
                    x2,
                    y2,
                    confidence
                )
            )

    # -------------------------------------------------
    # YOLO RAW OUTPUT
    #
    # Usually:
    # (1, 84, 8400)
    #
    # First four values:
    # x, y, width, height
    #
    # Remaining values:
    # class scores
    # -------------------------------------------------

    else:

        raw_output = np.squeeze(
            output
        )

        if raw_output.ndim != 2:

            print(
                "Unsupported model output shape:",
                output.shape
            )

            break

        # Convert:
        # (84, 8400)
        #
        # into:
        # (8400, 84)

        if raw_output.shape[0] < raw_output.shape[1]:

            predictions = raw_output.T

        else:

            predictions = raw_output

        if predictions.shape[1] < 6:

            print(
                "Unexpected detection format:",
                predictions.shape
            )

            break

        # Get class scores
        class_scores = predictions[:, 4:]

        # Find strongest class for each candidate
        best_class_ids = np.argmax(
            class_scores,
            axis=1
        )

        best_class_scores = np.max(
            class_scores,
            axis=1
        )

        candidate_boxes = []
        candidate_scores = []

        for index in range(
            len(predictions)
        ):

            best_class_id = int(
                best_class_ids[index]
            )

            confidence = float(
                best_class_scores[index]
            )

            # Person must be the strongest class
            if best_class_id != PERSON_CLASS_ID:
                continue

            if confidence < CONFIDENCE_THRESHOLD:
                continue

            center_x = float(
                predictions[index, 0]
            )

            center_y = float(
                predictions[index, 1]
            )

            box_width = float(
                predictions[index, 2]
            )

            box_height = float(
                predictions[index, 3]
            )

            x1 = (
                center_x
                - (box_width / 2)
            )

            y1 = (
                center_y
                - (box_height / 2)
            )

            candidate_boxes.append(
                [
                    x1,
                    y1,
                    box_width,
                    box_height
                ]
            )

            candidate_scores.append(
                confidence
            )

        # Remove overlapping detections
        selected_indices = cv2.dnn.NMSBoxes(
            candidate_boxes,
            candidate_scores,
            CONFIDENCE_THRESHOLD,
            NMS_THRESHOLD
        )

        if len(selected_indices) > 0:

            for selected in selected_indices:

                index = int(
                    np.asarray(
                        selected
                    ).flatten()[0]
                )

                x = candidate_boxes[
                    index
                ][0]

                y = candidate_boxes[
                    index
                ][1]

                box_width = candidate_boxes[
                    index
                ][2]

                box_height = candidate_boxes[
                    index
                ][3]

                x1 = x
                y1 = y

                x2 = (
                    x
                    + box_width
                )

                y2 = (
                    y
                    + box_height
                )

                x1, y1, x2, y2 = (
                    convert_box_to_original(
                        x1,
                        y1,
                        x2,
                        y2,
                        scale,
                        pad_x,
                        pad_y,
                        frame_width,
                        frame_height
                    )
                )

                persons.append(
                    (
                        x1,
                        y1,
                        x2,
                        y2,
                        candidate_scores[index]
                    )
                )

    # -------------------------------------------------
    # DISPLAY PERSON DETECTIONS
    # -------------------------------------------------

    current_person_count = len(
        persons
    )

    for (
        x1,
        y1,
        x2,
        y2,
        confidence
    ) in persons:

        cv2.rectangle(
            display_frame,
            (x1, y1),
            (x2, y2),
            (255, 255, 255),
            2
        )

        cv2.putText(
            display_frame,
            f"Person {confidence:.2f}",
            (
                x1,
                max(20, y1 - 10)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    # Report only when detection state changes
    if (
        current_person_count > 0
        and not person_detected
    ):

        person_detected = True

        print(
            f"PERSON DETECTED! "
            f"Count: {current_person_count}"
        )

    elif (
        current_person_count == 0
        and person_detected
    ):

        person_detected = False

        print(
            "PERSON NO LONGER DETECTED"
        )

    # Display current number of people
    cv2.putText(
        display_frame,
        f"People: {current_person_count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "Project Sentinel - Person Detection",
        display_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()