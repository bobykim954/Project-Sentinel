import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Could not open camera.")
    exit()

previous_frame = None
frame_count = 0

CHANGE_THRESHOLD = 20

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read frame.")
        break

    frame_count = frame_count + 1

    # Convert current frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Compare current frame with previous frame
    if previous_frame is not None:

        difference = cv2.absdiff(previous_frame, gray_frame)

        change_level = difference.mean()

        if change_level >= CHANGE_THRESHOLD:
            print(f"CHANGE DETECTED! Level: {change_level:.2f}")

    # Store current frame
    previous_frame = gray_frame

    cv2.imshow("Project Sentinel - Scene Change Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()