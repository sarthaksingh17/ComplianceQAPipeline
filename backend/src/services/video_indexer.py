import os
import logging
import yt_dlp
import whisper

logger = logging.getLogger("video-indexer")


class VideoIndexerService:
    """
    LOCAL video processing service:
    - Downloads YouTube video
    - Transcribes using Whisper
    """

    def __init__(self):
        logger.info("Initializing Local Video Indexer Service...")
        self.model = whisper.load_model("base")
        logger.info("Whisper model loaded successfully")

    
    # Download YouTube Video
    
    def download_youtube_video(self, url, output_path="temp_video.%(ext)s"):
        """
        Downloads YouTube video locally and returns actual saved file path.
        """

        logger.info(f"Downloading YouTube video: {url}")

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": output_path,
            "quiet": True,
            "noplaylist": True,
            "merge_output_format": "mp4",
            "overwrites": True,
            "ffmpeg_location" : r"C:\ffmpeg\bin"
            
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)

            if not downloaded_file.endswith(".mp4"):
                downloaded_file = os.path.splitext(downloaded_file)[0] + ".mp4"

            logger.info(f"Video saved as: {downloaded_file}")
            return downloaded_file

        except Exception as e:
            logger.error(f"YouTube video download failed: {str(e)}")
            raise

    
    # Transcribe using Whisper
    
    def transcribe_video(self, video_path):
        logger.info("Starting transcription using Whisper...")
        

        try:
            # Force ffmpeg absolute path
            os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

            result = self.model.transcribe(video_path)
            transcript = result.get("text", "")

            logger.info("Transcription completed successfully")
            return transcript

        except Exception as e:
            logger.error(f"Whisper transcription failed: {str(e)}")
            raise

    
    # Cleanup
    
    def cleanup(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("Temporary video file removed")