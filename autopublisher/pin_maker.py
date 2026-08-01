import os
import random
import re

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PINS_MD = os.path.join(BASE_DIR, "pinterest", "pins.md")
OUT_DIR = os.path.join(BASE_DIR, "pinterest", "images")

W, H = 1000, 1500

GRADIENTS = [
    ((88, 28, 135), (37, 117, 252)),
    ((0, 128, 128), (8, 145, 178)),
    ((156, 39, 176), (63, 81, 181)),
    ((183, 28, 28), (245, 124, 0)),
    ((0, 105, 92), (29, 161, 242)),
    ((21, 101, 192), (0, 172, 193)),
]

FONT_MAIN = "C:/Windows/Fonts/ariblk.ttf"
FONT_FALLBACK = "C:/Windows/Fonts/arialbd.ttf"

BOT_LINK = "@m3lmhermes_bot"
BRAND = "WALEDNET"


def font(size):
    for path in (FONT_MAIN, FONT_FALLBACK):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_gradient(draw, top, bottom):
    for y in range(H):
        t = y / (H - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def wrap(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw_text_width(trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_text_width(text, fnt):
    return fnt.getbbox(text)[2] - fnt.getbbox(text)[0]


def deco(draw, seed):
    rnd = random.Random(seed)
    for _ in range(5):
        x = rnd.randint(-150, W - 50)
        y = rnd.randint(-150, H - 50)
        d = rnd.randint(120, 420)
        alpha_color = (255, 255, 255, 18)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([x, y, x + d, y + d], fill=alpha_color)
        return overlay
    return None


def make_pin(text, index, out_path):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    top, bottom = GRADIENTS[index % len(GRADIENTS)]
    draw_gradient(d, top, bottom)

    d = ImageDraw.Draw(img)
    rnd = random.Random(index)
    for _ in range(6):
        x = rnd.randint(-200, W - 100)
        y = rnd.randint(-200, H - 100)
        sz = rnd.randint(150, 500)
        d.ellipse([x, y, x + sz, y + sz], outline=(255, 255, 255, 40), width=3)
    for _ in range(4):
        x = rnd.randint(0, W - 60)
        y = rnd.randint(0, H - 60)
        d.ellipse([x, y, x + 60, y + 60], fill=(255, 255, 255, 25))

    fnt_brand = font(42)
    d.text((60, 70), BRAND, font=fnt_brand, fill=(255, 255, 255, 230))
    d.line([(60, 130), (360, 130)], fill=(255, 255, 255, 180), width=5)

    fnt_main = font(88)
    lines = wrap(text.upper(), fnt_main, W - 140)
    lines = lines[:6]
    y = 300
    for ln in lines:
        tw = draw_text_width(ln, fnt_main)
        d.text(((W - tw) / 2, y), ln, font=fnt_main, fill=(255, 255, 255, 255))
        y += 118

    fnt_btn = font(46)
    btn_text = "TAP TO OPEN"
    tw = draw_text_width(btn_text, fnt_btn)
    bx0, by0, bx1, by1 = (W - tw) / 2 - 50, H - 260, (W - tw) / 2 + tw + 50, H - 180
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=35, fill=(255, 255, 255, 255))
    d.text(((W - tw) / 2, H - 248), btn_text, font=fnt_btn, fill=top)

    fnt_link = font(38)
    tw = draw_text_width(BOT_LINK, fnt_link)
    d.text(((W - tw) / 2, H - 120), BOT_LINK, font=fnt_link, fill=(255, 255, 255, 230))

    img.save(out_path, quality=92)


def parse_pins():
    with open(PINS_MD, encoding="utf-8") as f:
        content = f.read()
    blocks = re.split(r"### Pin \d+", content)
    pins = []
    for b in blocks:
        m = re.search(r"Image text:\s*(.+)", b)
        if m:
            pins.append(m.group(1).strip().strip('"'))
    return pins


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    pins = parse_pins()
    if not pins:
        print("no pins found in pins.md")
        return 1
    for i, text in enumerate(pins):
        path = os.path.join(OUT_DIR, f"pin_{i + 1:02d}.jpg")
        make_pin(text, i, path)
        print(f"generated {path}: {text}")
    print(f"done: {len(pins)} images -> {OUT_DIR}")


if __name__ == "__main__":
    main()
