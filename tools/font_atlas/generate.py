#!/usr/bin/env python3
"""
Tạo bitmap font atlas tiếng Việt có dấu (UTF-8) dùng chung cho nhiều game.

Xuất:
  - atlas.png          : sprite sheet (nền trong suốt)
  - atlas.json         : metadata glyph (unicode, vị trí, metrics)
  - atlas.bin          : binary pack cho engine C/DOS (tùy chọn)
  - lookup.h           : header C tra cứu nhanh theo UTF-8

Dùng DejaVu Sans (hoặc font TTF bất kỳ hỗ trợ tiếng Việt).
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


@dataclass
class Glyph:
    char: str
    codepoint: int
    x: int
    y: int
    width: int
    height: int
    advance: int
    bearing_x: int
    bearing_y: int


def load_chars(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    seen: set[str] = set()
    chars: list[str] = []
    for ch in text:
        if ch in ("\n", "\r", "\t"):
            continue
        if ch not in seen:
            seen.add(ch)
            chars.append(ch)
    return chars


def measure_glyph(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.FreeTypeFont,
    ch: str,
    cell_w: int,
    cell_h: int,
) -> tuple[int, int, int, int, int, int]:
    """Trả về (width, height, advance, bearing_x, bearing_y, baseline)."""
    bbox = draw.textbbox((0, 0), ch, font=font)
    left, top, right, bottom = bbox
    w = right - left
    h = bottom - top

    # advance = khoảng cách con trỏ; dùng getlength nếu có
    try:
        advance = int(round(font.getlength(ch)))
    except AttributeError:
        advance = w

    # bearing: offset từ góc cell tới glyph
    bearing_x = -left
    bearing_y = -top

    return w, h, advance, bearing_x, bearing_y, bottom


def pack_grid(glyphs_info: list[tuple[str, int, int]], cols: int) -> list[tuple[int, int]]:
    positions = []
    for i, (_, gw, gh) in enumerate(glyphs_info):
        col = i % cols
        row = i // cols
        # dùng cell size cố định = max trong batch
        positions.append((col, row))
    return positions


def generate_atlas(
    chars: list[str],
    font_path: Path,
    font_size: int,
    padding: int,
    cols: int,
) -> tuple[Image.Image, list[Glyph], int, int]:
    font = ImageFont.truetype(str(font_path), font_size)

    # đo tất cả glyph trước
    probe = Image.new("L", (font_size * 4, font_size * 4), 0)
    probe_draw = ImageDraw.Draw(probe)

    measured: list[tuple[str, int, int, int, int, int, int]] = []
    max_w = max_h = 0
    for ch in chars:
        w, h, adv, bx, by, _ = measure_glyph(probe_draw, font, ch, 0, 0)
        cell_w = w + padding * 2
        cell_h = h + padding * 2
        max_w = max(max_w, cell_w)
        max_h = max(max_h, cell_h)
        measured.append((ch, w, h, adv, bx, by, cell_w))

    cell_w = max_w
    cell_h = max_h
    rows = (len(chars) + cols - 1) // cols
    atlas_w = cols * cell_w
    atlas_h = rows * cell_h

    atlas = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(atlas)
    glyphs: list[Glyph] = []

    for i, (ch, w, h, adv, bx, by, _) in enumerate(measured):
        col = i % cols
        row = i // cols
        cx = col * cell_w + padding
        cy = row * cell_h + padding

        # vẽ chữ trắng, anti-alias cho Win95; game DOS thường threshold về 1-bit sau
        draw.text((cx + bx - padding, cy + by - padding), ch, font=font, fill=(255, 255, 255, 255))

        glyphs.append(
            Glyph(
                char=ch,
                codepoint=ord(ch),
                x=col * cell_w,
                y=row * cell_h,
                width=cell_w,
                height=cell_h,
                advance=adv,
                bearing_x=bx,
                bearing_y=by,
            )
        )

    return atlas, glyphs, cell_w, cell_h


def write_json(
    out: Path,
    glyphs: list[Glyph],
    cell_w: int,
    cell_h: int,
    font_size: int,
    atlas_size: tuple[int, int],
) -> None:
    data = {
        "version": 1,
        "encoding": "utf-8",
        "font_size": font_size,
        "cell_width": cell_w,
        "cell_height": cell_h,
        "atlas_width": atlas_size[0],
        "atlas_height": atlas_size[1],
        "glyphs": [
            {
                "char": g.char,
                "codepoint": g.codepoint,
                "x": g.x,
                "y": g.y,
                "width": g.width,
                "height": g.height,
                "advance": g.advance,
                "bearing_x": g.bearing_x,
                "bearing_y": g.bearing_y,
            }
            for g in glyphs
        ],
    }
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_bin(out: Path, glyphs: list[Glyph], cell_w: int, cell_h: int, atlas_w: int, atlas_h: int) -> None:
    """
  Binary format (little-endian):
    magic     : 4s  'DVNF'
    version   : u16
    cell_w    : u16
    cell_h    : u16
    atlas_w   : u16
    atlas_h   : u16
    count     : u16
    [glyph record x count]:
      codepoint : u32
      x, y      : u16, u16
      advance   : u16
      bearing_x : i16
      bearing_y : i16
    """
    with out.open("wb") as f:
        f.write(b"DVNF")
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<HHHH", cell_w, cell_h, atlas_w, atlas_h))
        f.write(struct.pack("<H", len(glyphs)))
        for g in glyphs:
            f.write(struct.pack("<I", g.codepoint))
            f.write(struct.pack("<HH", g.x, g.y))
            f.write(struct.pack("<H", g.advance))
            f.write(struct.pack("<hh", g.bearing_x, g.bearing_y))


def write_header(out: Path, glyphs: list[Glyph]) -> None:
    lines = [
        "// Auto-generated Vietnamese font lookup",
        "#pragma once",
        "#include <stdint.h>",
        "",
        "typedef struct {",
        "    uint32_t codepoint;",
        "    uint16_t x, y;",
        "    uint16_t advance;",
        "    int16_t bearing_x, bearing_y;",
        "} ViGlyph;",
        "",
        f"#define VI_GLYPH_COUNT {len(glyphs)}",
        "",
        "static const ViGlyph VI_GLYPHS[] = {",
    ]
    for g in glyphs:
        esc = g.char.replace("\\", "\\\\").replace("'", "\\'")
        lines.append(
            f"    {{0x{g.codepoint:04X}, {g.x}, {g.y}, {g.advance}, {g.bearing_x}, {g.bearing_y}}}, /* '{esc}' */"
        )
    lines.append("};")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    here = Path(__file__).resolve().parent
    default_font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

    parser = argparse.ArgumentParser(description="Tạo bitmap font atlas tiếng Việt")
    parser.add_argument("--chars", type=Path, default=here / "chars_vi.txt")
    parser.add_argument("--font", type=Path, default=default_font)
    parser.add_argument("--size", type=int, default=16, help="Cỡ font pixel (12/14/16 phổ biến game TQ)")
    parser.add_argument("--padding", type=int, default=1)
    parser.add_argument("--cols", type=int, default=16)
    parser.add_argument("--out", type=Path, default=here.parent.parent / "output" / "font_16")
    parser.add_argument("--1bit", dest="one_bit", action="store_true", help="Chuyển atlas sang đen trắng 1-bit (DOS)")
    args = parser.parse_args()

    if not args.font.exists():
        print(f"Font không tồn tại: {args.font}", file=sys.stderr)
        return 1

    chars = load_chars(args.chars)
    atlas, glyphs, cell_w, cell_h = generate_atlas(chars, args.font, args.size, args.padding, args.cols)

    if args.one_bit:
        # threshold cho VGA mode text replacement
        gray = atlas.convert("L")
        bw = gray.point(lambda p: 255 if p > 128 else 0, mode="1")
        atlas = bw.convert("RGBA")

    args.out.mkdir(parents=True, exist_ok=True)
    atlas.save(args.out / "atlas.png")
    write_json(args.out / "atlas.json", glyphs, cell_w, cell_h, args.size, atlas.size)
    write_bin(args.out / "atlas.bin", glyphs, cell_w, cell_h, atlas.size[0], atlas.size[1])
    write_header(args.out / "vi_glyphs.h", glyphs)

    print(f"Đã tạo {len(glyphs)} glyph → {args.out}")
    print(f"  Atlas: {atlas.size[0]}x{atlas.size[1]} px, cell {cell_w}x{cell_h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
