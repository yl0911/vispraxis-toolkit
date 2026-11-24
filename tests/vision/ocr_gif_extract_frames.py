"""Extract all frames from the historical OCR GIF sample."""
from pathlib import Path
from scripts.vision.extract_gif_frames import run
SOURCE=Path(r"D:\yl\desktop\test\vg_ocr_gif\test\gif\QFNqjKU.gif");OUTPUT=Path(r"C:\Users\Administrator\Desktop\test11")
def main()->int:
    try:r=run(SOURCE,OUTPUT,step=1,partitions=1)
    except (ImportError,OSError,ValueError) as e:print(f"ERROR: {e}");return 1
    print(f"gifs={r.gifs} frames={r.frames}");return 0
if __name__=="__main__":raise SystemExit(main())
