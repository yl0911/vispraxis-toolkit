"""Extract frames every two seconds from the historical video directory."""
from pathlib import Path
from scripts.vision.extract_video_frames import run
SOURCE=Path(r"F:\video");OUTPUT=Path(r"F:\video_cut");INTERVAL_SECONDS=2
def main()->int:
    try:r=run(SOURCE,OUTPUT,interval=INTERVAL_SECONDS,interval_seconds=True)
    except (ImportError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(f"videos={r.videos} frames={r.frames} failed={r.failed}");return 0 if not r.failed else 1
if __name__=="__main__":raise SystemExit(main())
