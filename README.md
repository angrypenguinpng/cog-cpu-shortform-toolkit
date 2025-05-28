# TikTok Video Processor 🎬

A powerful video processing toolkit built with FFmpeg and Cog, designed specifically for TikTok and short-form content creation.

## Features

### 🎯 TikTok-Focused Tasks
- **`make_vertical`** - Convert horizontal videos to 9:16 TikTok format
- **`add_background_music`** - Mix background audio with existing video audio
- **`image_to_video`** - Create videos from images with Ken Burns zoom effect
- **`slideshow`** - Turn multiple images into video slideshow
- **`trim_to_length`** - Cut videos to specific durations (15s, 30s, 60s)
- **`trim_to_audio`** - Trim video to match audio track length
- **`speed_to_fit`** - Adjust video speed to match audio duration

### 📹 Original Video Tasks
- Format conversion (MP4, GIF, etc.)
- Video reversal and bounce effects
- Audio extraction and frame extraction

## Quick Start

### Local Development
```bash
# Install dependencies with UV
uv sync

# Build the container
cog build

# Start server
cog run -p 5000 python -m cog.server.http

# Test all tasks
python samples.py

