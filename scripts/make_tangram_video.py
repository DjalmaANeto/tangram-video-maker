#!/usr/bin/env python3
import os
import sys
import subprocess
import random
import time
from PIL import Image, ImageDraw, ImageEnhance

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 make_tangram_video.py <input_video.mp4> [output_name.mp4]")
        sys.exit(1)

    input_video = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else "tangram_video.mp4"
    
    output_dir = "/data/data/com.termux/files/home/downloads"
    os.makedirs(output_dir, exist_ok=True)
    output_video = os.path.join(output_dir, output_name)

    if not os.path.exists(input_video):
        print(f"Error: Input video '{input_video}' not found.")
        sys.exit(1)

    print(f"Processing input video: {input_video}")

    # 1. Probe video metadata
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_video
    ]
    res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    lines = res.stdout.strip().splitlines()
    width = int(lines[0])
    height = int(lines[1])
    fps_parts = lines[2].split('/')
    fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else float(fps_parts[0])
    duration = float(lines[3])

    target_fps = 30
    total_frames = int(duration * target_fps)
    print(f"Resolution: {width}x{height}, FPS: {fps:.2f}, Duration: {duration:.2f}s -> {total_frames} frames")

    # 2. Extract frames and audio
    temp_dir = "/data/data/com.termux/files/home/.gemini/tmp/tangram_skill"
    frames_dir = os.path.join(temp_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    print("Extracting video frames...")
    subprocess.run([
        "ffmpeg", "-y", "-i", input_video,
        "-vf", f"fps={target_fps},scale={width}:{height},setsar=1",
        os.path.join(frames_dir, "frame_%04d.jpg")
    ], check=True)

    extracted_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.jpg')])
    num_frames = len(extracted_files)
    if num_frames == 0:
        print("Error: No frames extracted.")
        sys.exit(1)

    # 3. Generate random mosaic triangulation (COLS=3, ROWS=4 -> 24 triangles covering width x height)
    COLS = 3
    ROWS = 4
    cell_w = width / COLS
    cell_h = height / ROWS

    grid_points = []
    for r in range(ROWS + 1):
        row_pts = []
        for c in range(COLS + 1):
            x = c * cell_w
            y = r * cell_h
            if 0 < c < COLS:
                x += random.uniform(-cell_w * 0.35, cell_w * 0.35)
            if 0 < r < ROWS:
                y += random.uniform(-cell_h * 0.35, cell_h * 0.35)
            row_pts.append((int(x), int(y)))
        grid_points.append(row_pts)

    triangles = []
    for r in range(ROWS):
        for c in range(COLS):
            p00 = grid_points[r][c]
            p01 = grid_points[r][c+1]
            p10 = grid_points[r+1][c]
            p11 = grid_points[r+1][c+1]
            triangles.append([p00, p01, p10])
            triangles.append([p01, p11, p10])

    tri_data = []
    for tri in triangles:
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.polygon(tri, fill=255)
        
        xs = [p[0] for p in tri]
        ys = [p[1] for p in tri]
        min_x, max_x = max(0, min(xs)), min(width, max(xs))
        min_y, max_y = max(0, min(ys)), min(height, max(ys))
        
        tri_data.append({
            "poly": tri,
            "mask": mask,
            "box": (min_x, min_y, max_x, max_y)
        })

    # 4. Render frames
    out_frames_dir = os.path.join(temp_dir, "out_frames")
    os.makedirs(out_frames_dir, exist_ok=True)

    print("Rendering Tangram mosaic frames...")
    t0 = time.time()
    for f_idx in range(num_frames):
        src_path = os.path.join(frames_dir, extracted_files[f_idx])
        base_img = Image.open(src_path).convert("RGB")
        bg_img = ImageEnhance.Brightness(base_img).enhance(0.45) # 45% brightness background
        
        canvas = bg_img.copy()
        draw_canvas = ImageDraw.Draw(canvas)
        
        for idx, tri_info in enumerate(tri_data):
            shift = int(idx * num_frames / len(triangles))
            mapped_f_idx = (f_idx + shift) % num_frames
            
            tri_src_path = os.path.join(frames_dir, extracted_files[mapped_f_idx])
            tri_src = Image.open(tri_src_path).convert("RGB")
            
            box = tri_info["box"]
            cropped_src = tri_src.crop(box)
            cropped_mask = tri_info["mask"].crop(box)
            
            canvas.paste(cropped_src, box[:2], cropped_mask)
            draw_canvas.polygon(tri_info["poly"], outline=(255, 255, 255), width=2)

        out_path = os.path.join(out_frames_dir, f"out_{f_idx:04d}.jpg")
        canvas.save(out_path, quality=90)

        if (f_idx + 1) % 50 == 0 or f_idx == num_frames - 1:
            print(f"Rendered {f_idx + 1}/{num_frames} frames ({(time.time()-t0):.1f}s)")

    # 5. Encode output video with original audio preservation
    temp_video = os.path.join(temp_dir, "temp_no_audio.mp4")
    print("Encoding video stream...")
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(target_fps),
        "-i", os.path.join(out_frames_dir, "out_%04d.jpg"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "23",
        temp_video
    ], check=True)

    print("Merging original audio and video...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", input_video,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0?",
        "-shortest",
        output_video
    ], check=True)

    print(f"Success! Tangram video saved at: {output_video}")

if __name__ == "__main__":
    main()
