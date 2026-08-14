#!/usr/bin/env python3
"""Phân tích / chuyển đổi đĩa CloneCD (.ccd + .img + .sub) cho Sango II."""

from __future__ import annotations

import argparse
import re
import struct
import sys
from pathlib import Path

SECTOR_RAW = 2352
SECTOR_SYNC = 16
SECTOR_USER = 2048


def parse_ccd(path: Path) -> dict:
    text = path.read_text(encoding="ascii", errors="replace")
    tracks: list[dict] = []
    current: dict | None = None
    end_lba = 0

    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"\[TRACK (\d+)\]", line)
        if m:
            current = {"num": int(m.group(1))}
            tracks.append(current)
            continue
        if current is None:
            m2 = re.match(r"PLBA=(\d+)", line)
            if m2 and "Point=0xa2" in text.split(line)[0][-200:]:
                pass
            continue
        if line.startswith("MODE="):
            current["mode"] = int(line.split("=", 1)[1])
        elif line.startswith("INDEX 1="):
            current["index1"] = int(line.split("=", 1)[1])

    for m in re.finditer(
        r"\[Entry \d+\][\s\S]*?Point=0xa2[\s\S]*?PLBA=(\d+)", text
    ):
        end_lba = int(m.group(1))

    for i, t in enumerate(tracks):
        start = t["index1"]
        end = tracks[i + 1]["index1"] if i + 1 < len(tracks) else end_lba
        t["start"] = start
        t["end"] = end
        t["sectors"] = end - start

    return {"tracks": tracks, "end_lba": end_lba, "volume_hint": "PIONEERV01"}


def lba_to_msf(lba: int) -> str:
    """MSF cho file CUE (Red Book: +150 pregap)."""
    lba += 150
    f = lba % 75
    s = (lba // 75) % 60
    m = lba // 75 // 60
    return f"{m:02d}:{s:02d}:{f:02d}"


def ccd_to_cue(ccd_path: Path, img_name: str | None = None) -> str:
    meta = parse_ccd(ccd_path)
    img = img_name or ccd_path.with_suffix(".img").name
    lines = [f'FILE "{img}" BINARY']
    for t in meta["tracks"]:
        if t["mode"] == 1:
            lines.append(f'  TRACK {t["num"]:02d} MODE1/2352')
        else:
            lines.append(f'  TRACK {t["num"]:02d} AUDIO')
        lines.append(f'    INDEX 01 {lba_to_msf(t["start"])}')
    return "\n".join(lines) + "\n"


def read_data_sector(img: Path, lba: int) -> bytes:
    with img.open("rb") as f:
        f.seek(lba * SECTOR_RAW)
        return f.read(SECTOR_RAW)[SECTOR_SYNC : SECTOR_SYNC + SECTOR_USER]


def read_extent(img: Path, extent: int, size: int) -> bytes:
    buf = b""
    sec = extent
    while len(buf) < size:
        buf += read_data_sector(img, sec)
        sec += 1
    return buf[:size]


def list_iso_dir(img: Path, extent: int, size: int) -> list[tuple[str, bool, int, int]]:
    data = read_extent(img, extent, size)
    pos = 0
    out: list[tuple[str, bool, int, int]] = []
    while pos < size:
        rec = data[pos]
        if rec == 0:
            pos += 1
            continue
        flags = data[pos + 25]
        ext = struct.unpack("<I", data[pos + 2 : pos + 6])[0]
        ln = struct.unpack("<I", data[pos + 10 : pos + 14])[0]
        name_len = data[pos + 32]
        name = data[pos + 33 : pos + 33 + name_len].decode("ascii", "replace")
        if name_len == 1:
            name = "." if data[pos + 33] == 0 else ".."
        if name not in (".", ".."):
            out.append((name, bool(flags & 2), ext, ln))
        pos += rec
    return out


def extract_file(img: Path, extent: int, size: int, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(read_extent(img, extent, size))


def extract_dir(img: Path, extent: int, size: int, dest: Path) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    for name, is_dir, ext, ln in list_iso_dir(img, extent, size):
        target = dest / name
        if is_dir:
            n += extract_dir(img, ext, ln, target)
        else:
            extract_file(img, ext, ln, target)
            n += 1
    return n


def cmd_analyze(args) -> int:
    ccd = args.ccd.resolve()
    img = ccd.with_suffix(".img")
    sub = ccd.with_suffix(".sub")
    meta = parse_ccd(ccd)

    print(f"Định dạng: CloneCD (bộ 3 file)")
    print(f"  {ccd.name}  — bảng track / TOC ({ccd.stat().st_size:,} B)")
    print(f"  {img.name}  — ảnh raw sector 2352B ({img.stat().st_size:,} B)")
    print(f"  {sub.name}  — subchannel 96B/frame ({sub.stat().st_size:,} B)")
    print()
    print("Đĩa gốc ngày xưa: CD-ROM vật lý (Mixed Mode)")
    print("  Track 1 = DATA (game, installer, CRACK/)")
    print("  Track 2-25 = AUDIO Redbook (nhạc nền — cần đĩa gắn mới phát)")
    print()

    for t in meta["tracks"]:
        kind = "DATA" if t["mode"] == 1 else "AUDIO"
        dur = t["sectors"] / 75
        print(
            f"  Track {t['num']:2d} {kind:5s}  "
            f"{lba_to_msf(t['start'])}  sectors={t['sectors']:6d}  ~{dur:.0f}s"
        )

    pvd = read_data_sector(img, 16)
    vol = pvd[40:71].decode("ascii", "replace").strip()
    root_ext = struct.unpack("<I", pvd[156 + 2 : 156 + 6])[0]
    root_sz = struct.unpack("<I", pvd[156 + 10 : 156 + 14])[0]
    root = list_iso_dir(img, root_ext, root_sz)

    games = [n for n, d, _, _ in root if d and n not in ("CRACK",)]
    print(f"\nVolume label: {vol}")
    print(f"Root: {len(root)} mục")
    print(f"Thư mục game/demo: {len(games)}")
    for name in sorted(games):
        print(f"  [DIR] {name}")
    print("  [DIR] CRACK  ← copy vào SANGO2 sau cài đặt")
    for key in ("SANGO.WAV", "INSTALL.BAT", "SAN2.GRP"):
        for n, d, e, s in root:
            if n.upper() == key:
                print(f"  file  {n} ({s:,} B)")
    return 0


def cmd_cue(args) -> int:
    cue_text = ccd_to_cue(args.ccd, args.img_name)
    out = args.output or args.ccd.with_suffix(".cue")
    out.write_text(cue_text, encoding="ascii")
    print(f"Wrote: {out}")
    print("DOSBox: imgmount d Sango2.cue -t cdrom")
    return 0


def cmd_extract(args) -> int:
    ccd = args.ccd.resolve()
    img = ccd.with_suffix(".img")
    out = args.output.resolve()
    meta = parse_ccd(ccd)
    t1 = meta["tracks"][0]

    pvd = read_data_sector(img, 16)
    root_ext = struct.unpack("<I", pvd[156 + 2 : 156 + 6])[0]
    root_sz = struct.unpack("<I", pvd[156 + 10 : 156 + 14])[0]

    if args.only == "crack":
        for name, is_dir, ext, ln in list_iso_dir(img, root_ext, root_sz):
            if is_dir and name.upper() == "CRACK":
                n = extract_dir(img, ext, ln, out / "CRACK")
                print(f"Extract CRACK/ → {out / 'CRACK'} ({n} files)")
                return 0
        print("Không thấy thư mục CRACK")
        return 1

    if args.only == "sango2-data":
        # File Sango II ở root CD (không cần nhạc track 2+)
        names = {
            "SANGO.WAV", "SANGO.TAB", "SAN2.GRP", "SAN2.VMC", "INSTALL.BAT",
            "INST.EXE", "SETSOUND.EXE", "FONT16.PAT", "FONT24.PAT",
        }
        n = 0
        for name, is_dir, ext, ln in list_iso_dir(img, root_ext, root_sz):
            if not is_dir and name.upper() in names:
                extract_file(img, ext, ln, out / name)
                n += 1
                print(f"  {name} ({ln:,} B)")
        print(f"Extract {n} file Sango2 data → {out}")
        return 0

    n = extract_dir(img, root_ext, root_sz, out)
    print(f"Extract full data track → {out} ({n} files)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CloneCD .ccd+.img+.sub — phân tích, chuyển CUE, extract data"
    )
    parser.add_argument("--ccd", type=Path, default=Path("Sango2.ccd"))
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_a = sub.add_parser("analyze", help="Phân tích cấu trúc đĩa")
    p_a.set_defaults(func=cmd_analyze)

    p_c = sub.add_parser("cue", help="Tạo Sango2.cue cho DOSBox (dùng chung .img)")
    p_c.add_argument("-o", "--output", type=Path)
    p_c.add_argument("--img-name", help="Tên file IMG trong CUE (mặc định Sango2.img)")
    p_c.set_defaults(func=cmd_cue)

    p_e = sub.add_parser("extract", help="Extract track DATA ra thư mục")
    p_e.add_argument("-o", "--output", type=Path, required=True)
    p_e.add_argument(
        "--only",
        choices=("all", "crack", "sango2-data"),
        default="all",
        help="all=full data track | crack=thư mục CRACK | sango2-data=file gốc Sango2",
    )
    p_e.set_defaults(func=cmd_extract)

    args = parser.parse_args()
    if not args.ccd.exists():
        print(f"Không thấy: {args.ccd}", file=sys.stderr)
        return 1
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
