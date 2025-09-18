from PIL import Image
from pathlib import Path

src = Path("assets/icon.png")   
dst = Path("assets/icon.ico")   # 目标 ico
img = Image.open(src).convert("RGBA")
sizes = [256, 128, 64, 48, 32, 16]
img.save(dst, sizes=[(s, s) for s in sizes])
print("Saved:", dst.resolve())
