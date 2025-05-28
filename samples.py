"""
To set up, first run a local cog server using:
 cog run -p 5000 python -m cog.server.http
Then, in a separate terminal, generate samples
 python samples.py
"""
import base64
import os
import sys
import requests
import glob
import time

def run(output_fn, **kwargs):
    if glob.glob(f"{output_fn.rsplit('.', 1)[0]}*"):
        print("Already ran", output_fn)
        return
    prediction_start = time.time()
    print("Running prediction", output_fn)
    url = "http://localhost:5000/predictions"
    response = requests.post(url, json={"input": kwargs})
    print(f"Prediction took: {time.time() - prediction_start:.2f}s")
    data = response.json()
    try:
        for i, datauri in enumerate(data["output"]):
            base64_encoded_data = datauri.split(",")[1]
            decoded_data = base64.b64decode(base64_encoded_data)
            with open(
                f"{output_fn.rsplit('.', 1)[0]}_{i}.{output_fn.rsplit('.', 1)[1]}", "wb"
            ) as f:
                f.write(decoded_data)
        print("Wrote", output_fn)
    except Exception as e:
        print("Error!", str(e))
        print("input:", kwargs)
        print(data["logs"])
        sys.exit(1)

def main():
    # Original tasks
    run(
        "sample_reverse_video.mp4",
        task="reverse_video",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )
    
    run(
        "sample_bounce_video.mp4",
        task="bounce_video",
        input_file="https://replicate.delivery/pbxt/CmppJesjwO3jPSmdd1fflCjGeODlOpVy5I0PyXlgLeMmanVRC/video.mp4",
    )
    
    run(
        "sample_bounce_gif.gif",
        task="bounce_video",
        input_file="https://replicate.delivery/pbxt/KCBdyVkWcgjiCM3nzdg9JpqX8xzTGUimj4mWdpWgCQOm6umr/replicate-prediction-3rcqh5dbvob5u7gsd5vammyfwy.gif",
    )
    
    run(
        "sample_extract_video_audio_as_mp3.mp3",
        task="extract_video_audio_as_mp3",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )
    
    run(
        "sample_convert_to_mp4.mp4",
        task="convert_input_to_mp4",
        input_file="https://replicate.delivery/pbxt/RU9CI33SMCKMFBFQplELLexGPsOGNIU42VpauosBZZLkhW2IA/tmp.gif",
    )
    
    run(
        "sample_convert_to_mp4_with_fps.mp4",
        task="convert_input_to_mp4",
        fps=1,
        input_file="https://replicate.delivery/pbxt/RU9CI33SMCKMFBFQplELLexGPsOGNIU42VpauosBZZLkhW2IA/tmp.gif",
    )
    
    run(
        "sample_convert_to_gif.gif",
        task="convert_input_to_gif",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )
    
    run(
        "sample_frames_to_mp4.mp4",
        task="zipped_frames_to_mp4",
        input_file="https://replicate.delivery/pbxt/IyPciuTwd9miRkQm3AVd4ZZrNta1i1M8rKs7vJtpy83uAIIi/frames.zip",
    )
    
    run(
        "sample_frames_to_mp4_with_fps.mp4",
        task="zipped_frames_to_mp4",
        fps=1,
        input_file="https://replicate.delivery/pbxt/IyPciuTwd9miRkQm3AVd4ZZrNta1i1M8rKs7vJtpy83uAIIi/frames.zip",
    )
    
    run(
        "sample_frames_to_gif.gif",
        task="zipped_frames_to_gif",
        input_file="https://replicate.delivery/pbxt/IyPciuTwd9miRkQm3AVd4ZZrNta1i1M8rKs7vJtpy83uAIIi/frames.zip",
    )
    
    run(
        "sample_frames_to_gif_with_fps.gif",
        task="zipped_frames_to_gif",
        fps=1,
        input_file="https://replicate.delivery/pbxt/IyPciuTwd9miRkQm3AVd4ZZrNta1i1M8rKs7vJtpy83uAIIi/frames.zip",
    )
    
    run(
        "sample_extract_frames_from_input.zip",
        task="extract_frames_from_input",
        fps=12,
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )

    # NEW TIKTOK TASKS
    
    # Make vertical (TikTok format)
    run(
        "sample_make_vertical.mp4",
        task="make_vertical",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )
    
    # Add background music
    run(
        "sample_with_background_music.mp4",
        task="add_background_music",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
        audio_file="https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",  # Replace with actual audio URL
        volume_ratio=0.3,
    )
    
    # Image to video with Ken Burns effect
    run(
        "sample_image_to_video.mp4",
        task="image_to_video",
        input_file="https://picsum.photos/1080/1920.jpg",  # Replace with actual image URL
        duration=15,
        fps=30,
    )
    
    # Image to video - longer duration
    run(
        "sample_image_to_video_long.mp4",
        task="image_to_video",
        input_file="https://picsum.photos/1920/1080.jpg",  # Replace with actual image URL
        duration=30,
        fps=24,
    )
    
    # Slideshow from images
    run(
        "sample_slideshow.mp4",
        task="slideshow",
        input_file="https://example.com/images.zip",  # Replace with actual zip URL containing images
        duration=20,
    )
    
    # Trim to specific length
    run(
        "sample_trim_to_15sec.mp4",
        task="trim_to_length",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
        duration=15,
    )
    
    # Trim to 30 seconds
    run(
        "sample_trim_to_30sec.mp4",
        task="trim_to_length",
        input_file="https://replicate.delivery/pbxt/CmppJesjwO3jPSmdd1fflCjGeODlOpVy5I0PyXlgLeMmanVRC/video.mp4",
        duration=30,
    )
    
    # Trim video to match audio length
    run(
        "sample_trim_to_audio.mp4",
        task="trim_to_audio",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
        audio_file="https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",  # Replace with actual audio URL
    )
    
    # Speed adjust to fit audio
    run(
        "sample_speed_to_fit.mp4",
        task="speed_to_fit",
        input_file="https://replicate.delivery/pbxt/CmppJesjwO3jPSmdd1fflCjGeODlOpVy5I0PyXlgLeMmanVRC/video.mp4",
        audio_file="https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",  # Replace with actual audio URL
    )
    
    # Combined workflow examples
    
    # Complete TikTok workflow: horizontal video    # Complete TikTok workflow: horizontal video → vertical + music + trim
    run(
        "sample_tiktok_workflow_1.mp4",
        task="make_vertical",
        input_file="https://replicate.delivery/pbxt/0hNQY7Gy2eSiG6ghDRkabuJeV4oDNETFB6cWi2NdfB2TdMvhA/out.mp4",
    )
    
    # Image → TikTok video with music
    run(
        "sample_image_tiktok_ready.mp4",
        task="image_to_video",
        input_file="https://picsum.photos/1080/1920.jpg",
        duration=25,
        fps=30,
    )


if __name__ == "__main__":
    main()
