import cv2
import numpy as np


# Detection configuration
PERSON_CLASS_ID = 0
PERSON_CONFIDENCE_THRESHOLD = 0.65
NMS_THRESHOLD = 0.55

INPUT_SIZE = (640, 640)


def letterbox(image, new_shape=INPUT_SIZE):
    """Resize an image while preserving its aspect ratio."""

    original_height, original_width = image.shape[:2]

    target_width, target_height = new_shape

    scale = min(
        target_width / original_width,
        target_height / original_height
    )

    resized_width = int(round(original_width * scale))
    resized_height = int(round(original_height * scale))

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

    return resized, scale, left, top


def convert_box_to_original(
    x1,
    y1,
    x2,
    y2,
    scale,
    pad_x,
    pad_y,
    original_width,
    original_height
):
    """Convert model coordinates back to camera coordinates."""

    x1 = (x1 - pad_x) / scale
    y1 = (y1 - pad_y) / scale
    x2 = (x2 - pad_x) / scale
    y2 = (y2 - pad_y) / scale

    x1 = max(0, min(int(round(x1)), original_width - 1))
    y1 = max(0, min(int(round(y1)), original_height - 1))
    x2 = max(0, min(int(round(x2)), original_width - 1))
    y2 = max(0, min(int(round(y2)), original_height - 1))

    return x1, y1, x2, y2


def detect_persons(frame, model):
    """
    Detect people in a camera frame using the YOLO ONNX model.

    Supports:
        (1, 300, 6)   End-to-end detections
        (1, 84, 8400) Raw YOLO detections

    Returns:
        List of dictionaries containing bounding boxes
        and confidence values.
    """

    original_height, original_width = frame.shape[:2]

    image, scale, pad_x, pad_y = letterbox(
        frame,
        INPUT_SIZE
    )

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    blob = cv2.dnn.blobFromImage(
        image,
        scalefactor=1 / 255.0,
        size=INPUT_SIZE,
        swapRB=False,
        crop=False
    )

    model.setInput(blob)

    outputs = model.forward()

    output = outputs

    if isinstance(outputs, (list, tuple)):
        output = outputs[0]

    output = np.asarray(output)

    detections = []

    # Format A: End-to-end YOLO output
    # [x1, y1, x2, y2, confidence, class_id]

    if output.ndim == 3 and output.shape[-1] == 6:

        rows = output[0]

        for row in rows:

            x1, y1, x2, y2, confidence, class_id = row

            confidence = float(confidence)
            class_id = int(class_id)

            if confidence < PERSON_CONFIDENCE_THRESHOLD:
                continue

            if class_id != PERSON_CLASS_ID:
                continue

            x1, y1, x2, y2 = convert_box_to_original(
                x1,
                y1,
                x2,
                y2,
                scale,
                pad_x,
                pad_y,
                original_width,
                original_height
            )

            width = max(0, x2 - x1)
            height = max(0, y2 - y1)

            if width <= 0 or height <= 0:
                continue

            detections.append({
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "confidence": confidence
            })

    # Format B: Standard raw YOLO output
    # 4 box values + 80 class scores

    elif output.ndim == 3 and output.shape[1] == 84:

        predictions = output[0].T

        boxes = []
        confidences = []

        for prediction in predictions:

            center_x = float(prediction[0])
            center_y = float(prediction[1])
            width = float(prediction[2])
            height = float(prediction[3])

            class_scores = prediction[4:]

            class_id = int(np.argmax(class_scores))
            confidence = float(class_scores[class_id])

            if class_id != PERSON_CLASS_ID:
                continue

            if confidence < PERSON_CONFIDENCE_THRESHOLD:
                continue

            x1 = center_x - width / 2
            y1 = center_y - height / 2
            x2 = center_x + width / 2
            y2 = center_y + height / 2

            x1, y1, x2, y2 = convert_box_to_original(
                x1,
                y1,
                x2,
                y2,
                scale,
                pad_x,
                pad_y,
                original_width,
                original_height
            )

            box_width = max(0, x2 - x1)
            box_height = max(0, y2 - y1)

            if box_width <= 0 or box_height <= 0:
                continue

            boxes.append([
                x1,
                y1,
                box_width,
                box_height
            ])

            confidences.append(confidence)

        if boxes:

            indices = cv2.dnn.NMSBoxes(
                boxes,
                confidences,
                PERSON_CONFIDENCE_THRESHOLD,
                NMS_THRESHOLD
            )

            if len(indices) > 0:

                for index in np.asarray(indices).flatten():

                    x, y, width, height = boxes[index]

                    detections.append({
                        "x1": int(x),
                        "y1": int(y),
                        "x2": int(x + width),
                        "y2": int(y + height),
                        "confidence": float(confidences[index])
                    })

    return detections