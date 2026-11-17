# Tangram Video Maker

An LLM-agnostic Python and FFmpeg utility that transforms any source video into a dynamic geometric Tangram / mosaic video while preserving the original video dimensions, proportions, and audio track.

## Implementation Details

The application is structured around a robust frame-processing and composition pipeline:

1. **Metadata Probing**: Uses `ffprobe` to inspect the source video's resolution (width/height), frame rate (FPS), and total duration.
2. **Frame & Audio Extraction**: Extracts frames at a target frame rate (default 30 FPS) using `ffmpeg`, preparing them for manipulation.
3. **Full-Dimension Geometric Mosaic**:
   - Generates a randomized triangular grid mesh spanning the entire canvas dimensions.
   - Computes precise polygon masks and optimized bounding boxes for each triangle using Pillow (`PIL`).
4. **Temporal Shifting & Composition**:
   - The original video plays in the background with reduced brightness (45%) for visual contrast.
   - Each geometric triangle in the mosaic displays a time-shifted segment of the video, ensuring that the entire video unfolds across the mosaic pieces simultaneously and progressively.
5. **Audio Re-integration**: Muxes the newly rendered video stream with the original audio track using `ffmpeg` (`-c:a aac`), ensuring perfect synchronization and zero audio loss.

---

## Requirements

- Python 3.x
- `Pillow` (Python Imaging Library)
- `numpy`
- `ffmpeg` & `ffprobe` installed and available in system PATH.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/DjalmaANeto/tangram-video-maker.git
cd tangram-video-maker
```

Install dependencies:

```bash
pip install Pillow numpy
```

---

## Usage

Run the script directly from the command line:

```bash
python3 scripts/make_tangram_video.py <path_to_input_video.mp4> [output_filename.mp4]
```

The output video will be automatically generated and saved in your `Downloads` folder.

---

## License

This project is open-source and available under the [MIT License](LICENSE).
