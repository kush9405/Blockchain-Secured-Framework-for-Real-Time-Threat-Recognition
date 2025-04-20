import cv2
import os
import time
import subprocess
import threading
from datetime import datetime
import hashlib
from cryptography.fernet import Fernet

class CameraAudioRecorder:
    def __init__(self, capture_duration=10, output_directory=".", camera_id=0, sample_rate=44100):
        """
        Initializes the CameraAudioRecorder.

        Args:
            capture_duration (int): The duration of each video capture segment in seconds.
            output_directory (str): The directory to save the recorded video and audio files.
            camera_id (int): The ID of the camera to use (usually 0 for the default camera).
            sample_rate (int): The sample rate for recording audio in Hz.
        """
        self.capture_duration = capture_duration
        self.output_directory = output_directory
        self.camera_id = camera_id
        self.sample_rate = sample_rate
        self.is_recording = False
        self.audio_process = None  # Store the audio recording process

    def record_audio(self, audio_output_path):
        """Records audio from the microphone using FFmpeg."""
        try:
            print("Recording audio...")
            command = [
                "ffmpeg",
                "-f", "avfoundation",  # Use macOS's AVFoundation for audio input
                "-i", ":0",  # Capture from default audio device (adjust if needed)
                "-acodec", "pcm_s16le",  # Audio codec
                "-ar", str(self.sample_rate),  # Sample rate
                "-t", str(self.capture_duration),  # Duration of recording
                audio_output_path
            ]

            self.audio_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = self.audio_process.communicate()
            print(f"FFmpeg (audio) stdout: {stdout}")
            print(f"FFmpeg (audio) stderr: {stderr}")
            if self.audio_process.returncode != 0:
                print(f"Error recording audio (FFmpeg return code: {self.audio_process.returncode})")
                return False

            print("Audio recording completed.")
            return True
        except Exception as e:
            print(f"Error recording audio: {e}")
            return False

    def record_video(self, video_output_path):
        """Records video from the camera using OpenCV."""
        try:
            cap = cv2.VideoCapture(self.camera_id)
            if not cap.isOpened():
                print(f"Error: Could not open camera with ID {self.camera_id}")
                return None

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Create VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(video_output_path, fourcc, fps, (width, height))

            start_time = time.time()
            while time.time() - start_time < self.capture_duration and self.is_recording:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame. Stopping recording.")
                    self.is_recording = False
                    break
                out.write(frame)

            out.release()
            cap.release()
            return True
        except Exception as e:
            print(f"Error recording video: {e}")
            return False

    def record_and_split(self):
        """Records video and audio, then combines them."""
        self.is_recording = True
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory, exist_ok=True)

        try:
            while self.is_recording:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_filename = os.path.join(self.output_directory, f"capture_{timestamp}.mp4")
                audio_filename = os.path.join(self.output_directory, f"audio_{timestamp}.wav")
                video_with_audio_filename = os.path.join(self.output_directory, f"video_with_audio_{timestamp}.mp4")

                audio_thread = threading.Thread(target=self.record_audio, args=(audio_filename,))
                video_thread = threading.Thread(target=self.record_video, args=(video_filename,))

                audio_thread.start()
                video_thread.start()
                audio_thread.join()
                video_thread.join()

                if os.path.exists(video_filename) and os.path.exists(audio_filename):
                    command = [
                        "ffmpeg",
                        "-i", video_filename,
                        "-i", audio_filename,
                        "-c:v", "copy",
                        "-c:a", "aac",
                        "-shortest",
                        video_with_audio_filename
                    ]
                    print(f"Combining audio and video into {video_with_audio_filename}")
                    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                return video_with_audio_filename
        except Exception as e:
            print(f"Error during recording: {e}")
        finally:
            self.is_recording = False

    def start_recording(self):
        """Starts the recording in a separate thread."""
        if not self.is_recording:
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self.record_and_split)
            self.recording_thread.start()
            print("Recording started.")
        else:
            print("Recording is already in progress.")

    def stop_recording(self):
        """Stops the recording."""
        if self.is_recording:
            self.is_recording = False
            if hasattr(self, 'recording_thread') and self.recording_thread.is_alive():
                self.recording_thread.join()
            if self.audio_process and self.audio_process.poll() is None:
                self.audio_process.terminate()
                self.audio_process.wait()
            print("Recording stopped.")
        else:
            print("No recording in progress.")

class BlockchainVideoEncryptor:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = {
            'index': 0,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data': 'Genesis Block',
            'previous_hash': '0'
        }
        genesis_block['hash'] = self.hash_block(genesis_block)
        self.chain.append(genesis_block)

    def hash_block(self, block):
        block_string = f"{block['index']}{block['timestamp']}{block['data']}{block['previous_hash']}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def create_new_block(self, data):
        previous_block = self.chain[-1]
        new_block = {
            'index': previous_block['index'] + 1,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data': data,
            'previous_hash': previous_block['hash']
        }
        new_block['hash'] = self.hash_block(new_block)
        self.chain.append(new_block)
        return new_block

    def encrypt_video(self, video_path):
        key = Fernet.generate_key()
        f = Fernet(key)

        try:
            with open(video_path, "rb") as video_file:
                video_data = video_file.read()
        except FileNotFoundError:
            print(f"Error: Video file not found at {video_path}")
            return None, None

        encrypted_data = f.encrypt(video_data)
        self.create_new_block({'video_file': os.path.basename(video_path), 'encryption_method': 'Fernet'})
        return encrypted_data, key

    def decrypt_video(self, encrypted_data, key):
        f = Fernet(key)
        return f.decrypt(encrypted_data)

    def print_blockchain(self):
        """Prints the details of the blockchain."""
        print("Blockchain:")
        for block in self.chain:
            print(block)

if __name__ == "__main__":
    recorder = CameraAudioRecorder(capture_duration=10, output_directory="recordings", camera_id=0, sample_rate=44100)
    
    # Start recording
    recorder.start_recording()
    time.sleep(15)  # Allow recording for 15 seconds
    recorder.stop_recording()

    # Get the video_with_audio_filename from the recording process
    video_with_audio_filename = recorder.record_and_split()

    if video_with_audio_filename and os.path.exists(video_with_audio_filename):
        encryptor = BlockchainVideoEncryptor()

        user_input = input("Do you want to encrypt the video using blockchain? (yes/no): ").strip().lower()
        if user_input == "yes":
            encrypted_data, encryption_key = encryptor.encrypt_video(video_with_audio_filename)
            if encrypted_data:
                # Create the encrypted_videos directory if it doesn't exist
                encrypted_directory = "encrypted_videos"
                if not os.path.exists(encrypted_directory):
                    os.makedirs(encrypted_directory, exist_ok=True)

                # Save the encrypted video with a timestamped filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                encrypted_filename = os.path.join(encrypted_directory, f"encrypted_video_{timestamp}.enc")
                with open(encrypted_filename, "wb") as encrypted_file:
                    encrypted_file.write(encrypted_data)
                print(f"Video encrypted successfully and saved as {encrypted_filename}.")
                print("Encryption key must be stored securely!")

                # Print the blockchain details
                encryptor.print_blockchain()

                # Decrypt the video as an example
                decrypt_input = input("Do you want to decrypt the video? (yes/no): ").strip().lower()
                if decrypt_input == "yes":
                    decrypted_data = encryptor.decrypt_video(encrypted_data, encryption_key)
                    decrypted_filename = os.path.join(encrypted_directory, f"decrypted_video_{timestamp}.mp4")
                    with open(decrypted_filename, "wb") as decrypted_file:
                        decrypted_file.write(decrypted_data)
                    print(f"Video decrypted successfully and saved as {decrypted_filename}.")
            else:
                print("Encryption failed.")
        else:
            print("Video encryption skipped.")
    else:
        print("Error: Video file not found or recording failed.")