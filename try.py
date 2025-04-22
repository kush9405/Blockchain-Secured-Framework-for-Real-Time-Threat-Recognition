import cv2

def list_available_cameras():
    """Lists all available cameras by checking their indices."""
    available_cameras = []
    for camera_id in range(10):  # Check camera IDs from 0 to 9
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            available_cameras.append(camera_id)
            cap.release()
    return available_cameras

if __name__ == "__main__":
    cameras = list_available_cameras()
    if cameras:
        print(f"Available cameras: {cameras}")
    else:
        print("No cameras found.")