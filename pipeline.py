import os
import cv2
import time

def get_user_input():
    """
    Function to get user input for processing.
    Returns 'yes' or 'no'.
    """
    while True:
        user_input = input("Do you want to continue recording? (yes/no): ").strip().lower()
        if user_input in ["yes", "no"]:
            return user_input
        print("Invalid input. Please type 'yes' or 'no'.")

def encrypt_with_blockchain(frame):
    """
    Function to encrypt a video frame using blockchain.
    Replace this with your actual blockchain encryption logic.
    """
    print("Encrypting video frame using blockchain...")
    # Blockchain encryption logic here
    # For now, just simulate encryption
    encrypted_frame = frame  # Placeholder for encrypted frame
    print("Encryption complete.")
    return encrypted_frame

def process_video_stream():
    """
    Process real-time video stream and encrypt frames based on user input.
    Records for 10 seconds, then asks the user if they want to continue.
    """
    cap = cv2.VideoCapture(0)  # Open webcam (use 0 for default camera)
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    print("Press 'q' to quit the video stream.")
    while True:
        start_time = time.time()  # Record the start time
        while time.time() - start_time < 10:  # Record for 10 seconds
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read frame from the camera.")
                break

            # Display the current frame
            cv2.imshow("Video Stream", frame)

            # Encrypt the frame (optional, based on your logic)
            encrypted_frame = encrypt_with_blockchain(frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return

        # Ask the user if they want to continue after 10 seconds
        user_input = get_user_input()
        if user_input == "no":
            print("Stopping the video stream.")
            break

    # Release the video capture and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Run the real-time video processing pipeline
    process_video_stream()