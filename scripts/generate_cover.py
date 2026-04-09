#!/usr/bin/env python3
"""
Generate a KDP-ready full cover wrap PDF (back + spine + front).

Reads title and author from config.json.
CUSTOMISE: Update PAGE_COUNT, back cover copy, colours, and COVER_IMG path.

Usage: python3 scripts/generate_cover.py
Output: output/<title>-cover-wrap.pdf
"""

import json
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
COVER_IMG = os.path.join(BASE_DIR, "images", "cover", "cover.jpg")

# --- Read config ---
with open(os.path.join(BASE_DIR, "config.json")) as f:
    CONFIG = json.load(f)

BOOK_TITLE = CONFIG["title"].upper()
BOOK_AUTHOR = CONFIG["author"].upper()
PAGE_COUNT = CONFIG.get("page_count", 150)  # Set in config.json; update after building paperback interior

# KDP specs
DPI = 300
BLEED = 0.125
TRIM_W = 6.0
TRIM_H = 9.0
SPINE_W = PAGE_COUNT * 0.0025  # cream paper formula

TOTAL_W = BLEED + TRIM_W + SPINE_W + TRIM_W + BLEED
TOTAL_H = BLEED + TRIM_H + BLEED
PX_W = round(TOTAL_W * DPI)
PX_H = round(TOTAL_H * DPI)
BLEED_PX = round(BLEED * DPI)
TRIM_W_PX = round(TRIM_W * DPI)
SPINE_W_PX = round(SPINE_W * DPI)

# CUSTOMISE: Your colour scheme
BG_COLOR = (30, 33, 39)
TEXT_COLOR = (255, 255, 255)
MUTED_COLOR = (180, 175, 168)

# CUSTOMISE: Back cover copy (manually line-broken to fit)
BACK_COVER_HEADLINE = "Your headline here.\nSecond line."
BACK_COVER_BODY = [
    "Your back cover copy goes here.",
    "Describe what the book is about",
    "and who it's for.",
    "",
    "Keep it to a few short paragraphs.",
    "This text needs to fit within the",
    "back cover safe zone.",
]
BACK_COVER_TAGLINE = "A closing line\nthat hooks the reader."
WEBSITE = "yourwebsite.com"


def find_font(names, size):
    dirs = ["/System/Library/Fonts/", "/System/Library/Fonts/Supplemental/", os.path.expanduser("~/Library/Fonts/")]
    for name in names:
        for d in dirs:
            for ext in [".ttf", ".ttc", ".otf"]:
                path = os.path.join(d, name + ext)
                if os.path.exists(path):
                    try:
                        return ImageFont.truetype(path, size)
                    except Exception:
                        continue
    return ImageFont.load_default()


def main():
    print(f"\n=== KDP Cover Wrap ===\n")
    print(f"  Dimensions: {TOTAL_W:.3f} x {TOTAL_H:.3f} inches ({PX_W} x {PX_H}px)")
    print(f"  Spine: {SPINE_W:.4f} inches for {PAGE_COUNT} pages")

    img = Image.new("RGB", (PX_W, PX_H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --- Front cover ---
    front_x = BLEED_PX + TRIM_W_PX + SPINE_W_PX
    if os.path.exists(COVER_IMG):
        print("  Loading front cover image...")
        cover = Image.open(COVER_IMG).convert("RGB")
        target_w = TRIM_W_PX + BLEED_PX
        target_h = PX_H
        scale = max(target_w / cover.width, target_h / cover.height)
        cover = cover.resize((round(cover.width * scale), round(cover.height * scale)), Image.LANCZOS)
        # Centre on trim area
        left = max(0, cover.width // 2 - TRIM_W_PX // 2 - BLEED_PX // 2)
        top = (cover.height - target_h) // 2
        cover = cover.crop((left, top, left + target_w, top + target_h))
        img.paste(cover, (front_x, 0))

    # --- Spine ---
    spine_x = BLEED_PX + TRIM_W_PX
    draw.rectangle([(spine_x, 0), (spine_x + SPINE_W_PX, PX_H)], fill=BG_COLOR)

    font_spine_title = find_font(["Georgia"], round(0.16 * DPI))
    font_spine_author = find_font(["Georgia"], round(0.11 * DPI))

    spine_img = Image.new("RGB", (round(TRIM_H * DPI), SPINE_W_PX), BG_COLOR)
    spine_draw = ImageDraw.Draw(spine_img)
    title_bbox = spine_draw.textbbox((0, 0), BOOK_TITLE, font=font_spine_title)
    author_bbox = spine_draw.textbbox((0, 0), BOOK_AUTHOR, font=font_spine_author)
    tw = title_bbox[2] - title_bbox[0]
    aw = author_bbox[2] - author_bbox[0]
    th = title_bbox[3] - title_bbox[1]
    ah = author_bbox[3] - author_bbox[1]
    gap = round(0.3 * DPI)
    total = tw + gap + aw
    sx = (spine_img.width - total) // 2
    sy = (SPINE_W_PX - max(th, ah)) // 2
    spine_draw.text((sx, sy), BOOK_TITLE, fill=TEXT_COLOR, font=font_spine_title)
    spine_draw.text((sx + tw + gap, sy + (th - ah) // 2), BOOK_AUTHOR, fill=MUTED_COLOR, font=font_spine_author)
    spine_img = spine_img.rotate(90, expand=True)
    img.paste(spine_img, (spine_x, BLEED_PX))

    # --- Back cover ---
    font_headline = find_font(["Georgia Bold", "Georgia"], round(0.28 * DPI))
    font_body = find_font(["Georgia"], round(0.15 * DPI))
    font_small = find_font(["Georgia"], round(0.11 * DPI))

    margin_left = BLEED_PX + round(0.6 * DPI)
    y = BLEED_PX + round(1.2 * DPI)

    for line in BACK_COVER_HEADLINE.split("\n"):
        draw.text((margin_left, y), line, fill=TEXT_COLOR, font=font_headline)
        bbox = draw.textbbox((0, 0), line, font=font_headline)
        y += (bbox[3] - bbox[1]) + round(0.08 * DPI)
    y += round(0.35 * DPI)

    for line in BACK_COVER_BODY:
        if not line:
            y += round(0.12 * DPI)
            continue
        draw.text((margin_left, y), line, fill=MUTED_COLOR, font=font_body)
        bbox = draw.textbbox((0, 0), line, font=font_body)
        y += (bbox[3] - bbox[1]) + round(0.06 * DPI)
    y += round(0.4 * DPI)

    for line in BACK_COVER_TAGLINE.split("\n"):
        draw.text((margin_left, y), line, fill=(210, 205, 198), font=font_body)
        bbox = draw.textbbox((0, 0), line, font=font_body)
        y += (bbox[3] - bbox[1]) + round(0.06 * DPI)

    url_y = PX_H - BLEED_PX - round(0.8 * DPI)
    url_bbox = draw.textbbox((0, 0), WEBSITE, font=font_small)
    url_w = url_bbox[2] - url_bbox[0]
    back_cx = BLEED_PX + TRIM_W_PX // 2
    draw.text((back_cx - url_w // 2, url_y), WEBSITE, fill=MUTED_COLOR, font=font_small)

    # --- Save ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_path = os.path.join(OUTPUT_DIR, f"{BOOK_TITLE.replace(' ', '-')}-cover-wrap.pdf")
    img_path = os.path.join(OUTPUT_DIR, ".cover-temp.png")
    img.save(img_path, dpi=(DPI, DPI))
    Image.open(img_path).save(pdf_path, "PDF", resolution=DPI)
    os.remove(img_path)

    print(f"\n  Generated: {os.path.basename(pdf_path)}")
    print(f"  Output: {pdf_path}\n")


if __name__ == "__main__":
    main()