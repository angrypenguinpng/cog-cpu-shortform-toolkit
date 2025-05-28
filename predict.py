from cog import BasePredictor, Input, Path
from typing import List
import subprocess
import os
import shutil
import zipfile

VIDEO_FILE_EXTENSIONS = [
    ".3g2",
    ".3gp",
    ".a64",
    ".avi",
    ".flv",
    ".gif",
    ".gifv",
    ".m2v",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".mv",
    ".mxf",
    ".nsv",
    ".ogg",
    ".ogv",
    ".rm",
    ".rmvb",
    ".roq",
    ".svi",
    ".vob",
    ".webm",
    ".wmv",
    ".yuv",
]

IMAGE_FILE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".tiff",
    ".webp",
]

AUDIO_FILE_EXTENSIONS = [
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".ogg",
    ".flac",
]

VIDEO_TASKS = [
    "convert_input_to_mp4",
    "convert_input_to_gif",
    "extract_video_audio_as_mp3",
    "extract_frames_from_input",
    "reverse_video",
    "bounce_video",
    "make_vertical",
    "add_background_music",
    "trim_to_length",
    "trim_to_audio",
    "speed_to_fit",
]

IMAGE_TASKS = [
    "image_to_video",
    "slideshow",
]

ZIP_TASKS = ["zipped_frames_to_mp4", "zipped_frames_to_gif"]


class Predictor(BasePredictor):
    def validate_inputs(self, task: str, input_file: Path, audio_file: Path = None):
        """Validate inputs"""
        if task in ZIP_TASKS:
            if input_file.suffix.lower() not in [".zip"]:
                raise ValueError("Input file must be a zip file")

        elif task in VIDEO_TASKS:
            if input_file.suffix.lower() not in VIDEO_FILE_EXTENSIONS:
                raise ValueError(
                    "Input file must be a video file with one of the following extensions: "
                    + ", ".join(VIDEO_FILE_EXTENSIONS)
                )

        elif task in IMAGE_TASKS:
            if task == "slideshow":
                if input_file.suffix.lower() != ".zip":
                    raise ValueError("For slideshow, input must be a zip file containing images")
            else:
                if input_file.suffix.lower() not in IMAGE_FILE_EXTENSIONS:
                    raise ValueError(
                        "Input file must be an image file with one of the following extensions: "
                        + ", ".join(IMAGE_FILE_EXTENSIONS)
                    )

        # Validate audio file if provided
        if audio_file and audio_file.suffix.lower() not in AUDIO_FILE_EXTENSIONS:
            raise ValueError(
                "Audio file must have one of the following extensions: "
                + ", ".join(AUDIO_FILE_EXTENSIONS)
            )

    def predict(
        self,
        task: str = Input(
            description="Task to perform",
            choices=[
                "convert_input_to_mp4",
                "convert_input_to_gif",
                "extract_video_audio_as_mp3",
                "zipped_frames_to_mp4",
                "zipped_frames_to_gif",
                "extract_frames_from_input",
                "reverse_video",
                "bounce_video",
                "make_vertical",
                "add_background_music",
                "image_to_video",
                "slideshow",
                "trim_to_length",
                "trim_to_audio",
                "speed_to_fit",
            ],
        ),
        input_file: Path = Input(description="File – zip, image or video to process"),
        audio_file: Path = Input(description="Audio file for background music (optional)", default=None),
        fps: int = Input(
            description="frames per second, if relevant. Use 0 to keep original fps (or use default). Converting to GIF defaults to 12fps",
            default=0,
        ),
        duration: int = Input(
            description="Duration in seconds for trim_to_length or image_to_video (default: 30)",
            default=30,
        ),
        volume_ratio: float = Input(
            description="Background music volume relative to original audio (0.1 = quiet, 1.0 = same level, 2.0 = louder)",
            default=0.3,
        ),
    ) -> List[Path]:
        """Run prediction"""
        if os.path.exists("/tmp/outputs"):
            shutil.rmtree("/tmp/outputs")
        os.makedirs("/tmp/outputs")

        self.validate_inputs(task, input_file, audio_file)
        self.fps = fps
        self.duration = duration
        self.volume_ratio = volume_ratio

        if task == "convert_input_to_mp4":
            return self.convert_video_to(input_file, "mp4")
        elif task == "convert_input_to_gif":
            return self.convert_video_to(input_file, "gif")
        elif task == "extract_video_audio_as_mp3":
            return self.extract_video_audio_as_mp3(input_file)
        elif task == "zipped_frames_to_mp4":
            return self.zipped_frames_to(input_file, "mp4")
        elif task == "zipped_frames_to_gif":
            return self.zipped_frames_to(input_file, "gif")
        elif task == "extract_frames_from_input":
            return self.extract_frames_from_input(input_file)
        elif task == "reverse_video":
            return self.reverse_video(input_file)
        elif task == "bounce_video":
            return self.bounce_video(input_file)
        elif task == "make_vertical":
            return self.make_vertical(input_file)
        elif task == "add_background_music":
            return self.add_background_music(input_file, audio_file)
        elif task == "image_to_video":
            return self.image_to_video(input_file)
        elif task == "slideshow":
            return self.slideshow(input_file)
        elif task == "trim_to_length":
            return self.trim_to_length(input_file)
        elif task == "trim_to_audio":
            return self.trim_to_audio(input_file, audio_file)
        elif task == "speed_to_fit":
            return self.speed_to_fit(input_file, audio_file)

        return []

    def get_video_duration(self, video_path: Path) -> float:
        """Get video duration in seconds using ffprobe"""
        command = [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path)
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return float(result.stdout.strip())

    def get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds using ffprobe"""
        return self.get_video_duration(audio_path)  # Same command works for audio

    def unzip(self, input_path: Path) -> List[Path]:
        """Unzip file"""
        print("Unzipping file")
        with zipfile.ZipFile(input_path, "r") as zip_ref:
            zip_ref.extractall("/tmp/outputs/zip")

        for filename in os.listdir("/tmp/outputs/zip"):
            os.rename(
                "/tmp/outputs/zip/" + filename,
                "/tmp/outputs/zip/" + filename.lower(),
            )

        print("Files in zip:")
        for filename in sorted(os.listdir("/tmp/outputs/zip")):
            print(filename)

    def run_ffmpeg(self, input, output_path: str, command: List[str]):
        """Run ffmpeg command"""

        prepend = ["ffmpeg"]
        if input:
            prepend.extend(["-i", str(input)])

        append = [output_path]
        command = prepend + command + append
        print("Running ffmpeg command: " + " ".join(command))
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "Command '{}' returned with error (code {}): {}".format(
                    e.cmd, e.returncode, e.output
                )
            )
        return [Path(output_path)]

    def convert_video_to(self, video_path: Path, type: str = "mp4") -> List[Path]:
        """Convert video to format using ffmpeg"""
        command = [
            "-pix_fmt",
            "yuv420p",  # Pixel format: YUV with 4:2:0 chroma subsampling
        ]

        if type == "gif":
            command.extend(
                [
                    "-vf",
                    f"fps={self.fps or 12},scale=512:-1:flags=lanczos",  # Set frame rate and scale
                    "-c:v",
                    "gif",  # Video codec: GIF
                ]
            )
        else:
            command.extend(
                [
                    "-c:v",
                    "libx264",  # Video codec: H.264
                    "-c:a",
                    "aac",  # Audio codec: AAC
                    "-q:a",
                    "0",  # Specify audio quality (0 is the highest)
                ]
            )

            if self.fps != 0:
                command.extend(["-r", str(self.fps)])

        return self.run_ffmpeg(video_path, f"/tmp/outputs/video.{type}", command)

    def extract_video_audio_as_mp3(self, video_path: Path) -> List[Path]:
        """Extract audio from video using ffmpeg"""
        command = [
            "-q:a",
            "0",  # Specify audio quality (0 is the highest)
            "-map",
            "a",  # Map audio tracks (ignore video)
        ]

        return self.run_ffmpeg(video_path, "/tmp/outputs/audio.mp3", command)

    def extract_frames_from_input(self, video_path: Path) -> List[Path]:
        """Extract frames from video using ffmpeg"""
        command = ["-vf", f"fps={self.fps}"] if self.fps != 0 else []
        self.run_ffmpeg(video_path, "/tmp/outputs/out%03d.png", command)

        output_files = []
        for filename in os.listdir("/tmp/outputs"):
            if filename.endswith(".png") and filename.startswith("out"):
                output_files.append(filename)

        with zipfile.ZipFile("/tmp/outputs/frames.zip", "w") as zip_ref:
            for filename in output_files:
                zip_ref.write(f"/tmp/outputs/{filename}", filename)

        return [Path("/tmp/outputs/frames.zip")]

    def zipped_frames_to(self, input_file: Path, type: str = "mp4") -> List[Path]:
        """Convert frames to video using ffmpeg"""
        self.unzip(input_file)
        frames_directory = "/tmp/outputs/zip"
        image_filetypes = ["jpg", "jpeg", "png"]
        frame_filetype = None
        for file in os.listdir(frames_directory):
            potential_filetype = file.split(".")[-1]
            if potential_filetype in image_filetypes:
                frame_filetype = potential_filetype
                break
        if frame_filetype is None:
            raise ValueError("No image files found in the zip file.")

        command = [
            "-framerate",
            str(12 if self.fps == 0 else self.fps),  # Set the frame rate
            "-pattern_type",
            "glob",  # Use glob pattern matching
            "-i",
            f"{frames_directory}/*.{frame_filetype}",
            "-pix_fmt",
            "yuv420p",  # Pixel format: YUV with 4:2:0 chroma subsampling
        ]

        if type == "gif":
            command.extend(
                [
                    "-vf",
                    "scale=512:-1:flags=lanczos",
                    "-c:v",
                    "gif",  # Video codec: GIF
                ]
            )
        else:
            command.extend(
                [
                    "-c:v",
                    "libx264",  # Video codec: H.264
                ]
            )

        return self.run_ffmpeg(False, f"/tmp/outputs/video.{type}", command)

    def reverse_video(self, video_path: Path) -> List[Path]:
        """Reverse video using ffmpeg"""
        output_file = "/tmp/outputs/reversed" + video_path.suffix
        command = [
            "-vf",
            "reverse",
            "-af",
            "areverse",
        ]

        return self.run_ffmpeg(video_path, output_file, command)

    def bounce_video(self, video_path: Path) -> List[Path]:
        """Bounce video or gif using ffmpeg"""
        reversed_video_path = "/tmp/outputs/reversed" + video_path.suffix
        self.reverse_video(video_path)

        with open("/tmp/outputs/concat_list.txt", "w") as f:
            f.write(f"file '{video_path}'\nfile '{reversed_video_path}'\n")

        command = [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "/tmp/outputs/concat_list.txt",  # Use the temporary file as input
        ]

        if video_path.suffix == ".gif":
            command.extend(
                [
                    "-vf",
                    "scale=512:-1:flags=lanczos",
                    "-c:v",
                    "gif",  # Video codec: GIF
                ]
            )
        else:
            command.extend(
                [
                    "-c",
                    "copy",
                ]
            )

        return self.run_ffmpeg(
            None, f"/tmp/outputs/bounced{video_path.suffix}", command
        )

    # NEW TIKTOK TASKS

    def make_vertical(self, video_path: Path) -> List[Path]:
        """Convert video to vertical 9:16 aspect ratio for TikTok"""
        command = [
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:a",
            "copy",
        ]
        return self.run_ffmpeg(video_path, "/tmp/outputs/vertical.mp4", command)

    def add_background_music(self, video_path: Path, audio_path: Path) -> List[Path]:
        """Add background music to video with volume mixing"""
        if not audio_path:
            raise ValueError("Audio file is required for add_background_music task")
        
        command = [
            "-i", str(audio_path),
            "-filter_complex",
            f"[0:a][1:a]amix=inputs=2:weights=1 {self.volume_ratio}[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",  # End when shortest input ends
        ]
        return self.run_ffmpeg(video_path, "/tmp/outputs/with_music.mp4", command)

    def image_to_video(self, image_path: Path) -> List[Path]:
        """Convert image to video with Ken Burns zoom effect"""
        fps_val = self.fps or 30
        command = [
            "-loop", "1",
            "-t", str(self.duration),
            "-framerate", str(fps_val),
            "-vf", 
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0015,1.5)':d={fps_val * self.duration}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
        ]
        return self.run_ffmpeg(image_path, "/tmp/outputs/image_video.mp4", command)

    def slideshow(self, zip_path: Path) -> List[Path]:
        """Create slideshow from zipped images"""
        self.unzip(zip_path)
        frames_directory = "/tmp/outputs/zip"
        
        # Find image files
        image_files = []
        for file in sorted(os.listdir(frames_directory)):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(f"{frames_directory}/{file}")
        
        if not image_files:
            raise ValueError("No image files found in zip")
        
        # Calculate duration per image
        duration_per_image = self.duration / len(image_files)
        
        # Create input list for ffmpeg
        with open("/tmp/outputs/slideshow_list.txt", "w") as f:
            for img in image_files:
                f.write(f"file '{img}'\nduration {duration_per_image}\n")
            # Add last image again for proper ending
            f.write(f"file '{image_files[-1]}'\n")
        
        command = [
            "-f", "concat",
            "-safe", "0",
            "-i", "/tmp/outputs/slideshow_list.txt",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
        ]
        return self.run_ffmpeg(None, "/tmp/outputs/slideshow.mp4", command)

    def trim_to_length(self, video_path: Path) -> List[Path]:
        """Trim video to specified duration"""
        command = [
            "-t", str(self.duration),
            "-c", "copy",
        ]
        return self.run_ffmpeg(video_path, "/tmp/outputs/trimmed.mp4", command)

    def trim_to_audio(self, video_path: Path, audio_path: Path) -> List[Path]:
        """Trim video to match audio duration"""
        if not audio_path:
            raise ValueError("Audio file is required for trim_to_audio task")
        
        audio_duration = self.get_audio_duration(audio_path)
        command = [
            "-t", str(audio_duration),
            "-c", "copy",
        ]
        return self.run_ffmpeg(video_path, "/tmp/outputs/trimmed_to_audio.mp4", command)

    def speed_to_fit(self, video_path: Path, audio_path: Path) -> List[Path]:
        """Adjust video speed to match audio duration"""
        if not audio_path:
            raise ValueError("Audio file is required for speed_to_fit task")
        
        video_duration = self.get_video_duration(video_path)
        audio_duration = self.get_audio_duration(audio_path)
        speed_factor = video_duration / audio_duration
        
        # Limit speed changes to reasonable range
        speed_factor = max(0.5, min(2.0, speed_factor))
        
        command = [
            "-filter_complex",
            f"[0:v]setpts={1/speed_factor}*PTS[v]; [0:a]atempo={speed_factor}[a]",
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-c:a", "aac",
        ]
        return self.run_ffmpeg(video_path, "/tmp/outputs/speed_fitted.mp4", command)