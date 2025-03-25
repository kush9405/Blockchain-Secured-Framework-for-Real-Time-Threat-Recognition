from moviepy.editor import VideoFileClip

def split_video_audio(video_path, audio_output_path, video_output_path):
    """
    Splits a video into audio and video components.

    Args:
        video_path: Path to the input video file.
        audio_output_path: Path to save the extracted audio.
        video_output_path: Path to save the video without audio.
    """
    try:
        video = VideoFileClip(video_path)

        # Extract audio
        video.audio.write_audiofile(audio_output_path)

        # Extract video without audio
        video.without_audio().write_videofile(video_output_path, codec="libx264")  # You may need to adjust the codec

        video.close()  #Important to properly release resources.
    except Exception as e:
        print(f"Error: {e}")

# Example usage:
video_file = "my_video.mp4"  # Replace with your video file
audio_file = "audio.mp3"
video_no_audio_file = "video_no_audio.mp4"

split_video_audio(video_file, audio_file, video_no_audio_file)
print("Splitting Completed")