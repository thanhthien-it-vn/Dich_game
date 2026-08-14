#!/usr/bin/env python3
"""
Trích chuỗi tiếng Trung/Nhật từ file binary game.

Quét byte sequence hợp lệ theo encoding (GBK, Shift-JIS…), xuất CSV để dịch.

Ví dụ:
  python3 extract_strings.py game.exe --encoding gbk -o strings_cn.csv
  python3 extract_strings.py data.dat --encoding shift_jis --min-len 4
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from encoding import decode, guess_encoding, is_cjk_char, normalize_encoding


def _valid_runs(data: bytes, encoding: str, min_len: int) -> list[tuple[int, str]]:
    enc = normalize_encoding(encoding)
    results: list[tuple[int, str]] = []
    i = 0
    n = len(data)

    while i < n:
        # Bỏ qua null padding
        if data[i] == 0:
            i += 1
            continue

        best_end = i
        best_text = ""

        # Thử mở rộng chuỗi từ vị trí i
        j = i
        buf = bytearray()
        while j < n:
            b = data[j]
            if b == 0:
                break
            # ASCII printable / CJK lead trail
            if b < 0x20 and b not in (0x09,):
                break
            buf.append(b)
            j += 1
            try:
                text = decode(bytes(buf), enc, errors="strict")
            except UnicodeDecodeError:
                continue
            cjk_count = sum(1 for c in text if is_cjk_char(c))
            if cjk_count >= min_len or (len(text) >= min_len and cjk_count > 0):
                best_end = j
                best_text = text

        if best_text and len(best_text.strip()) >= min_len:
            cjk = sum(1 for c in best_text if is_cjk_char(c))
            if cjk >= 1:
                results.append((i, best_text))
                i = best_end
                continue
        i += 1

    return results


def dedupe(strings: list[tuple[int, str]]) -> list[tuple[int, str]]:
    seen: set[str] = set()
    out: list[tuple[int, str]] = []
    for offset, text in strings:
        t = text.strip()
        if t and t not in seen:
            seen.add(t)
            out.append((offset, t))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Trích chuỗi CJK/JP từ binary game")
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--out", type=Path, help="CSV output (key, offset, text)")
    parser.add_argument("--encoding", "-e", help="gbk | shift_jis | big5 | auto")
    parser.add_argument("--min-len", type=int, default=2, help="Tối thiểu ký tự CJK")
    parser.add_argument("--limit", type=int, default=5000)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Không tìm thấy: {args.input}", file=sys.stderr)
        return 1

    data = args.input.read_bytes()
    enc = args.encoding or guess_encoding(data) or "gbk"
    enc = normalize_encoding(enc)
    print(f"Encoding: {enc}, size: {len(data)} bytes")

    found = dedupe(_valid_runs(data, enc, args.min_len))[: args.limit]
    print(f"Tìm thấy {len(found)} chuỗi (min CJK={args.min_len})")

    rows = [(f"0x{off:06X}", str(off), text) for off, text in found]

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["key", "offset", "text"])
            w.writerows(rows)
        print(f"→ {args.out}")
    else:
        for key, _, text in rows[:30]:
            safe = text.replace("\n", "\\n")[:80]
            print(f"  {key}: {safe}")
        if len(rows) > 30:
            print(f"  ... và {len(rows) - 30} chuỗi nữa (dùng -o để xuất hết)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
