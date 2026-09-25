import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Could not open camera.")
    exit()

previous_frame = None
frame_count = 0

CHANGE_THRESHOLD = 20
NO_CHANGE_FRAMES_TO_END = 30

event_active = False
no_change_frames = 0

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read frame.")
        break

    frame_count = frame_count + 1

    # Convert the current frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # We need a previous frame before we can compare anything
    if previous_frame is not None:

        difference = cv2.absdiff(previous_frame, gray_frame)

        change_level = difference.mean()

        if change_level >= CHANGE_THRESHOLD:
            no_change_frames = 0

            # Start a new event only once
            if not event_active:
                event_active = True

                print(
                    f"EVENT STARTED! Change level: {change_level:.2f}"
                )

        else:
            # Count how long the scene stays below the threshold
            if event_active:
                no_change_frames = no_change_frames + 1

                # End the event after a period of no significant change
                if no_change_frames >= NO_CHANGE_FRAMES_TO_END:
                    event_active = False
                    no_change_frames = 0

                    print("EVENT ENDED")

    # Store the current frame for the next comparison
    previous_frame = gray_frame

    cv2.imshow("Project Sentinel - Event Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()