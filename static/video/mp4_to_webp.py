import cv2
from PIL import Image
import argparse
import os
import glob


def mp4_to_webp(input_path, output_path=None, fps=None, max_frames=None, quality=80, loop=0):
    """Convert MP4 video to animated WebP using cv2 + Pillow."""
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {input_path}")

    orig_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    target_fps = fps if fps else orig_fps

    print(f"[{os.path.basename(input_path)}] FPS={orig_fps:.1f}, Frames={total_frames}, Target FPS={target_fps:.1f}")

    frames = []
    frame_interval = max(1, round(orig_fps / target_fps))
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count % frame_interval == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame_rgb))
            if max_frames and len(frames) >= max_frames:
                break
        count += 1

    cap.release()

    if not frames:
        raise ValueError("No frames extracted from video")

    print(f"  Extracted {len(frames)} frames")

    duration_ms = int(1000 / target_fps)
    first_frame = frames[0]
    other_frames = frames[1:]

    first_frame.save(
        output_path,
        save_all=True,
        append_images=other_frames,
        duration=duration_ms,
        loop=loop,
        quality=quality,
        method=6  # best compression
    )

    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"  Saved: {output_path} ({file_size_kb:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Convert MP4 to animated WebP")
    parser.add_argument("--input", "-i", type=str, default=None,
                        help="Input MP4 file or directory (default: current dir, all .mp4)")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help="Output WebP file or directory (default: same dir as input)")
    parser.add_argument("--fps", type=float, default=None,
                        help="Target FPS (default: original FPS)")
    parser.add_argument("--max-frames", type=int, default=None,
                        help="Max frames to extract")
    parser.add_argument("--quality", type=int, default=80,
                        help="WebP quality 0-100 (default: 80)")
    parser.add_argument("--no-loop", action="store_true",
                        help="Disable looping")
    args = parser.parse_args()

    loop = 0 if not args.no_loop else 1

    if args.input and os.path.isdir(args.input):
        mp4_files = sorted(glob.glob(os.path.join(args.input, "*.mp4")))
        if not mp4_files:
            print(f"No .mp4 files found in {args.input}")
            return
        out_dir = args.output if args.output else args.input
        os.makedirs(out_dir, exist_ok=True)
        for mp4 in mp4_files:
            name = os.path.splitext(os.path.basename(mp4))[0]
            out_path = os.path.join(out_dir, f"{name}.webp")
            mp4_to_webp(mp4, out_path, args.fps, args.max_frames, args.quality, loop)
    elif args.input:
        out_path = args.output if args.output else os.path.splitext(args.input)[0] + ".webp"
        mp4_to_webp(args.input, out_path, args.fps, args.max_frames, args.quality, loop)
    else:
        # Default: convert all mp4 in current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mp4_files = sorted(glob.glob(os.path.join(script_dir, "*.mp4")))
        if not mp4_files:
            print(f"No .mp4 files found in {script_dir}")
            return
        for mp4 in mp4_files:
            out_path = os.path.splitext(mp4)[0] + ".webp"
            mp4_to_webp(mp4, out_path, args.fps, args.max_frames, args.quality, loop)


if __name__ == "__main__":
    main()
