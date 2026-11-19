#!/usr/bin/env python3
"""Turn a finished frame video into the site's media set.

Usage:  python3 tools/add_frame.py SOURCE.mp4 KEY
Creates media/KEY.mp4 (720x1280, sound), media/KEY.jpg (poster),
media/preview/KEY.mp4 (12 s silent hover clip) and media/ptiles/KEY-0..7.jpg (9:16 tiles),
then prints the duration as m:ss for frames.json.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIT = "scale=720:1280:force_original_aspect_ratio=decrease:flags=lanczos,pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"


def run(*a):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *a], check=True)


def main(src, key):
    src = str(pathlib.Path(src).resolve())
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", src]))
    dur = float(info["format"]["duration"])
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    m = ROOT / "media"
    (m / "preview").mkdir(exist_ok=True); (m / "ptiles").mkdir(exist_ok=True)
    audio = ["-c:a", "aac", "-b:a", "128k"] if has_audio else ["-an"]
    run("-i", src, "-vf", FIT + ",fps=30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", *audio, str(m / f"{key}.mp4"))
    run("-ss", str(min(2, dur / 3)), "-i", str(m / f"{key}.mp4"), "-frames:v", "1", "-q:v", "4", str(m / f"{key}.jpg"))
    run("-i", str(m / f"{key}.mp4"), "-t", "12", "-an", "-vf", "scale=360:640,fps=24", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(m / "preview" / f"{key}.mp4"))
    for i in range(8):
        t = dur * (0.06 + 0.88 * i / 7)
        run("-ss", f"{t:.2f}", "-i", str(m / f"{key}.mp4"), "-frames:v", "1", "-vf", "scale=252:448", "-q:v", "5", str(m / "ptiles" / f"{key}-{i}.jpg"))
    print(json.dumps({"key": key, "duration": f"{int(dur // 60)}:{int(round(dur % 60)):02d}"}))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
