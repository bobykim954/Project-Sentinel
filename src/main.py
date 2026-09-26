import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Could not open camera.")
    exit()

previous_frame = None
frame_count = 0

# Minimum percentage of changed pixels required
REGION_MOTION_THRESHOLD = 3.0

# Number of consecutive frames required to confirm an event
START_CONFIRM_FRAMES = 2

# Number of quiet frames required to end an event
NO_CHANGE_FRAMES_TO_END = 30

event_active = False
no_change_frames = 0

candidate_region = None
start_confirm_frames = 0

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read frame.")
        break

    frame_count += 1

    height, width = frame.shape[:2]

    # Convert to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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

        # Ignore very small pixel changes
        _, motion_mask = cv2.threshold(
            difference,
            25,
            255,
            cv2.THRESH_BINARY
        )

        # Remove isolated noise
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (3, 3)
        )

        motion_mask = cv2.morphologyEx(
            motion_mask,
            cv2.MORPH_OPEN,
            kernel
        )

        # Divide the frame into four regions
        mid_x = width // 2
        mid_y = height // 2

        top_left = motion_mask[0:mid_y, 0:mid_x]
        top_right = motion_mask[0:mid_y, mid_x:width]
        bottom_left = motion_mask[mid_y:height, 0:mid_x]
        bottom_right = motion_mask[mid_y:height, mid_x:width]

        regions = {
            "TOP LEFT": top_left,
            "TOP RIGHT": top_right,
            "BOTTOM LEFT": bottom_left,
            "BOTTOM RIGHT": bottom_right
        }

        # Calculate motion percentage in each region
        region_scores = {}

        for name, region in regions.items():
            changed_pixels = cv2.countNonZero(region)
            total_pixels = region.size

            motion_percentage = (
                changed_pixels / total_pixels
            ) * 100

            region_scores[name] = motion_percentage

        # Find the region with the most motion
        active_region = max(
            region_scores,
            key=region_scores.get
        )

        motion_level = region_scores[active_region]

        # -----------------------------
        # EVENT START CONFIRMATION
        # -----------------------------
        if motion_level >= REGION_MOTION_THRESHOLD:

            no_change_frames = 0

            if not event_active:

                # Check whether the same region remains active
                if candidate_region == active_region:
                    start_confirm_frames += 1
                else:
                    candidate_region = active_region
                    start_confirm_frames = 1

                # Start event after consecutive confirmation frames
                if start_confirm_frames >= START_CONFIRM_FRAMES:

                    event_active = True
                    start_confirm_frames = 0
                    candidate_region = None

                    print(
                        f"EVENT STARTED! "
                        f"Region: {active_region} | "
                        f"Motion: {motion_level:.2f}%"
                    )

        else:

            # Reset start confirmation when motion disappears
            candidate_region = None
            start_confirm_frames = 0

            # -----------------------------
            # EVENT END DETECTION
            # -----------------------------
            if event_active:

                no_change_frames += 1

                if no_change_frames >= NO_CHANGE_FRAMES_TO_END:

                    event_active = False
                    no_change_frames = 0

                    print("EVENT ENDED")

        # Draw vertical region boundary
        cv2.line(
            frame,
            (mid_x, 0),
            (mid_x, height),
            (255, 255, 255),
            1
        )

        # Draw horizontal region boundary
        cv2.line(
            frame,
            (0, mid_y),
            (width, mid_y),
            (255, 255, 255),
            1
        )

        # Display strongest region and motion level
        cv2.putText(
            frame,
            f"{active_region}: {motion_level:.2f}%",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

    # Save current frame for the next comparison
    previous_frame = gray_frame

    cv2.imshow(
        "Project Sentinel - Motion Location",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()