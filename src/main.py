import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Could not open camera.")
    exit()

frame_count = 0

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read frame.")
        break

    frame_count = frame_count + 1

    if frame_count % 30 == 0:
        height, width, channels = frame.shape

        brightness = frame.mean()

        print(f"Width: {width}")
        print(f"Height: {height}")
        print(f"Channels: {channels}")
        print(f"Average Brightness: {brightness:.2f}")

    cv2.imshow("Project Sentinel - Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()