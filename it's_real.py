import cv2
import os
import time
import subprocess
import threading
from datetime import datetime

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
                return False # To exit the program

            print("Audio recording completed.")
            return True
        except Exception as e:
            print(f"Error recording audio: {e}")
            return False

    def record_video(self, video_output_path):
        """Records video from the camera using FFmpeg."""
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
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') #or AVC1
            out = cv2.VideoWriter(video_output_path, fourcc, fps, (width, height))

            start_time = time.time()
            while time.time() - start_time < self.capture_duration and self.is_recording:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame. Stopping recording.")
                    self.is_recording = False
                    break
                out.write(frame)
            # Release resources, while trying not to create a problem
            out.release()
            cap.release()
            return True
        except Exception as e:
            print(f"Error: Could not read camera {e}")

    def record_and_split(self):
            """Records video from the camera and combines it with separate recorded audio."""
            self.is_recording = True
            if os.path.exists("recordings") == False:
                os.makedirs("recordings", exist_ok=True) #The Recordings folder to properly run to.
            try:
                while self.is_recording:
                    # Generate Filenames
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    video_filename = os.path.join(self.output_directory, f"capture_{timestamp}.mp4")
                    audio_filename = os.path.join(self.output_directory, f"audio_{timestamp}.wav")
                    video_with_audio_filename = os.path.join(self.output_directory, f"video_with_audio_{timestamp}.mp4") # Change this for another check if everything works
                     # Record audio
                    audio_thread = threading.Thread(target=self.record_audio, args = (audio_filename,)) #Audio THread
                    video_thread = threading.Thread(target=self.record_video, args=(video_filename,)) # Video Thread
                    # Start both of the THREADS
                    audio_thread.start()
                    video_thread.start()
                    audio_thread.join() # Wait to Join threads.
                    video_thread.join()
                     # Use FFmpeg to put the audio file to the Video Filename with audio
                    if os.path.exists(video_filename) == True and os.path.exists(audio_filename) == True:
                        command = [
                            "ffmpeg",
                            "-i", video_filename, # Set Video
                            "-i", audio_filename, #SetAudio
                            "-c:v", "copy",  # Copy video stream
                            "-c:a", "aac",  # Encode the audio stream
                            "-shortest", # Make it as short as possible
                            video_with_audio_filename  # Output
                            ]
                        print(f"Attempting to mux audio and video to {video_with_audio_filename}")
                        combine_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text = True)
                        print(f"FFmpeg (mux) stdout: {combine_process.stdout}")
                        print(f"FFmpeg (mux) stderr: {combine_process.stderr}")

            except Exception as e:
                print(f"Error: General Error happened {e}")
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
                self.recording_thread.join()  # Wait for thread to finish
            if self.audio_process and self.audio_process.poll() is None: #To properly stop it
                self.audio_process.terminate() #To Kill it
                self.audio_process.wait()
            print("Recording stopped.")
        else:
            print("No recording in progress.")

if __name__ == "__main__":
    try:
      # Example usage:
      recorder = CameraAudioRecorder(capture_duration=10, output_directory="recordings", camera_id=0, sample_rate = 44100) #You can increase this to whatever you like

      recorder.start_recording()

      # Keep the main thread running for a while (e.g., 30 seconds) to allow recording
      time.sleep(30)

      recorder.stop_recording()

    except Exception as e:
        print(f"These packages are the packages that are not installed. {e}")
        print("Please do pip install, or refer to the instructions to setup. Please note there is a potential issue that MoviePy, may not properly load")