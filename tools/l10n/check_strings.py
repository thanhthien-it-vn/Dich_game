#!/usr/bin/env python3
"""
Kiểm tra chuỗi dịch tiếng Việt so với bản gốc (độ dài pixel).

Giúp phát hiện text tràn UI trước khi patch game.

Ví dụ:
  python3 check_strings.py --atlas output/win95_16/atlas.json \\
      --original strings_cn.csv --translated strings_vi.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


def load_atlas(path: Path) -> dict[int, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {g["codepoint"]: g for g in data["glyphs"]}


def text_width(text: str, glyphs: dict[int, dict], default: int) -> int:
    total = 0
    for ch in text:
        g = glyphs.get(ord(ch))
        total += g["advance"] if g else default
    return total


def read_pairs(original: Path, translated: Path) -> list[tuple[str, str, str]]:
    """Trả về (key, original, translated)."""
    if original.suffix.lower() == ".csv":
        orig_rows = list(csv.DictReader(original.open(encoding="utf-8")))
        trans_rows = list(csv.DictReader(translated.open(encoding="utf-8")))
        trans_map = {r.get("key", r.get("id", "")): r.get("text", r.get("vi", "")) for r in trans_rows}
        pairs = []
        for row in orig_rows:
            key = row.get("key", row.get("id", ""))
            pairs.append((key, row.get("text", row.get("cn", "")), trans_map.get(key, "")))
        return pairs

    orig_lines = original.read_text(encoding="utf-8").splitlines()
    trans_lines = translated.read_text(encoding="utf-8").splitlines()
    return [(str(i), o, t) for i, (o, t) in enumerate(zip(orig_lines, trans_lines))]


def main() -> int:
    parser = argparse.ArgumentParser(description="So sánh độ rộng chuỗi dịch")
    parser.add_argument("--atlas", type=Path, required=True)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--translated", type=Path, required=True)
    parser.add_argument("--ratio", type=float, default=1.0, help="Cho phép rộng hơn gốc tối đa X lần")
    parser.add_argument("--out", type=Path, help="Ghi báo cáo ra file")
    args = parser.parse_args()

    glyphs = load_atlas(args.atlas)
    default_adv = glyphs.get(ord("中"), glyphs.get(ord("A"), {"advance": 16}))["advance"]
    pairs = read_pairs(args.original, args.translated)

    warnings: list[str] = []
    for key, orig, trans in pairs:
        if not trans:
            continue
        w_orig = text_width(orig, glyphs, default_adv)
        w_trans = text_width(trans, glyphs, default_adv)
        limit = max(w_orig, 1) * args.ratio
        if w_trans > limit:
            warnings.append(
                f"[{key}] {w_trans}px > {limit:.0f}px (gốc {w_orig}px)\n"
                f"  CN: {orig[:60]}\n"
                f"  VI: {trans[:60]}"
            )

    report = "\n\n".join(warnings) if warnings else "OK — không có chuỗi vượt giới hạn."
    print(report)
    if args.out:
        args.out.write_text(report + "\n", encoding="utf-8")
    return 1 if warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
