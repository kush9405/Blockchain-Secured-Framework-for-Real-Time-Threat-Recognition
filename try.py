import cv2

def test_camera_access(camera_id):
    cap = cv2.VideoCapture(camera_id)
    if cap.isOpened():
        print(f"Camera {camera_id} is accessible.")
        cap.release()
    else:
        print(f"Camera {camera_id} is not accessible.")

def capture_photo(camera_id, output_path):
    """Captures a photo from the specified camera."""
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"Error: Camera {camera_id} is not accessible.")
        return

    print(f"Accessing camera {camera_id}...")
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_path, frame)
        print(f"Photo captured and saved to {output_path}")
    else:
        print("Error: Failed to capture photo.")

    cap.release()

def record_video(camera_id, output_path, duration=10):
    """Records a video from the specified camera."""
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"Error: Camera {camera_id} is not accessible.")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30  # Default to 30 FPS if not available

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    print(f"Recording video from camera {camera_id} for {duration} seconds...")
    frame_count = 0
    max_frames = duration * fps

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        out.write(frame)
        frame_count += 1

    # Release resources
    cap.release()
    out.release()
    print(f"Video recorded and saved to {output_path}")

if __name__ == "__main__":
    for camera_id in range(2):  # Test camera IDs from 0 to 9
        test_camera_access(camera_id)
    camera_id = 1  # Use camera index 1
    output_path = "captured_photo.jpg"  # Path to save the photo
    capture_photo(camera_id, output_path)
    output_path = "recorded_video.mp4"  # Path to save the video
    duration = 10  # Duration of the video in seconds
    record_video(camera_id, output_path, duration)