---
name: tangram-video-maker
description: Automatically creates a full-dimension geometric Tangram / mosaic video from any input video while preserving original video proportions, dimensions, and audio. Use when the user wants to generate a Tangram style video mosaic where the original video plays in the background and segmented views play across geometric polygon pieces.
---

# Tangram Video Maker

This skill automatically generates a geometric Tangram mosaic video from any source video file.

## Features

- **Preserves Original Proportions & Dimensions**: Automatically probes the input video resolution and maintains exact aspect ratio.
- **Preserves Original Audio**: Automatically extracts and merges the audio track from the source video into the final output.
- **Full-Dimension Mosaic**: Creates a geometric triangular mosaic covering the entire video frame, with the original video playing dimly in the background and different time-shifted video segments playing across each mosaic piece.
- **Output Location**: Saves the generated video directly into the user's `Downloads` folder.

## Usage

Run the bundled python script:

```bash
python3 scripts/make_tangram_video.py <input_video_path> [output_filename.mp4]
```
