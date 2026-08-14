#!/usr/bin/env python3
"""
Dich_game — CLI chính.

Một entry point cho toàn bộ pipeline. Chạy từ toolkit, trỏ tới thư mục game.

Ví dụ:
  python3 dich.py init ../games/MyRPG --encoding gbk
  python3 dich.py extract --game ../games/MyRPG
  python3 dich.py build-font --game ../games/MyRPG
  python3 dich.py fit --game ../games/MyRPG
  python3 dich.py pipeline --game ../games/MyRPG
  python3 dich.py status --game ../games/MyRPG
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

TOOLKIT = Path(__file__).resolve().parent


def load_game_config(game_root: Path) -> dict:
    cfg_path = game_root / "dich.game.json"
    if not cfg_path.exists():
        print(f"Không tìm thấy {cfg_path}", file=sys.stderr)
        print(f"Chạy: python3 dich.py init {game_root}", file=sys.stderr)
        sys.exit(1)
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def _run(cmd: list[str], desc: str) -> int:
    print(f"\n── {desc} ──")
    print(" ", " ".join(cmd))
    return subprocess.call(cmd, cwd=TOOLKIT)


def cmd_init(args) -> int:
    cmd = [sys.executable, str(TOOLKIT / "scripts" / "init_game.py"), str(args.game)]
    if args.encoding:
        cmd += ["--encoding", args.encoding]
    if args.profile:
        cmd += ["--profile", args.profile]
    if args.name:
        cmd += ["--name", args.name]
    if args.link_game:
        cmd += ["--link-game", str(args.link_game)]
    return subprocess.call(cmd)


def cmd_extract(args) -> int:
    cfg = load_game_config(args.game)
    game_dir = args.game / cfg["paths"]["game_dir"]
    out = args.game / cfg["files"]["extracted"]
    out.parent.mkdir(parents=True, exist_ok=True)

    # Tìm binary lớn nhất trong game/
    candidates = list(game_dir.glob("*.exe")) + list(game_dir.glob("*.dat")) + list(game_dir.glob("*.bin"))
    if not candidates:
        candidates = [p for p in game_dir.rglob("*") if p.suffix.lower() in (".exe", ".dat", ".bin", ".pak")]
    if not candidates:
        print(f"Không tìm thấy binary trong {game_dir}", file=sys.stderr)
        return 1

    target = max(candidates, key=lambda p: p.stat().st_size)
    return _run([
        sys.executable, str(TOOLKIT / "tools/l10n/extract_strings.py"),
        str(target), "-e", cfg["encoding"], "-o", str(out),
    ], f"Extract từ {target.name}")


def cmd_build_font(args) -> int:
    cfg = load_game_config(args.game)
    profile = TOOLKIT / "profiles" / f"{cfg['font_profile']}.json"
    if not profile.exists():
        print(f"Profile không tồn tại: {profile}", file=sys.stderr)
        return 1

    font_dir = args.game / cfg["paths"]["font_dir"]
    font_dir.mkdir(parents=True, exist_ok=True)

    # Gom ký tự từ bản dịch nếu có
    vi_csv = args.game / cfg["files"]["translated"]
    chars_out = args.game / "strings" / "chars.txt"
    chars_src = TOOLKIT / "tools/font_atlas/chars_vi.txt"

    if vi_csv.exists() and vi_csv.stat().st_size > 20:
        _run([
            sys.executable, str(TOOLKIT / "tools/l10n/collect_chars.py"),
            str(vi_csv), "--merge", str(chars_src), "-o", str(chars_out),
        ], "Gom ký tự từ bản dịch")

    cmd = [
        sys.executable, str(TOOLKIT / "tools/font_atlas/generate.py"),
        "--profile", str(profile),
        "--out", str(font_dir),
    ]
    if chars_out.exists():
        cmd += ["--chars", str(chars_out)]

    insured = args.game / cfg["files"].get("insured", "strings/insured.csv")
    preview = "Chào mừng! HP MP — tiếng Việt có dấu."
    if insured.exists():
        import csv
        with insured.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            if rows:
                preview = rows[0].get("text_insured", rows[0].get("text", preview))
    cmd += ["--preview", preview[:60]]

    return _run(cmd, f"Build font → {font_dir}")


def cmd_fit(args) -> int:
    cfg = load_game_config(args.game)
    atlas = args.game / cfg["paths"]["font_dir"] / "atlas.json"
    if not atlas.exists():
        print("Chưa có font — chạy build-font trước", file=sys.stderr)
        return 1

    orig = args.game / cfg["files"]["extracted"]
    vi = args.game / cfg["files"]["translated"]
    out = args.game / cfg["files"]["insured"]

    if not vi.exists():
        print(f"Chưa có bản dịch: {vi}", file=sys.stderr)
        return 1

    return _run([
        sys.executable, str(TOOLKIT / "tools/l10n/fit_insurance_cli.py"),
        "--csv", str(vi),
        "--original", str(orig),
        "--atlas", str(atlas),
        "--source", cfg["encoding"],
        "--cell", str(cfg.get("cell_width", 16)),
        "-o", str(out),
    ], "Fit 3 tầng bảo hiểm")


def cmd_check(args) -> int:
    cfg = load_game_config(args.game)
    atlas = args.game / cfg["paths"]["font_dir"] / "atlas.json"
    return _run([
        sys.executable, str(TOOLKIT / "tools/l10n/check_strings.py"),
        "--atlas", str(atlas),
        "--original", str(args.game / cfg["files"]["extracted"]),
        "--translated", str(args.game / cfg["files"]["translated"]),
        "--source", cfg["encoding"],
    ], "Kiểm tra tràn UI")


def cmd_pipeline(args) -> int:
    steps = [cmd_extract, cmd_build_font, cmd_fit]
    if args.with_check:
        steps.append(cmd_check)
    for fn in steps:
        rc = fn(args)
        if rc != 0:
            return rc
    print("\n✓ Pipeline xong.")
    cmd_status(args)
    return 0


def cmd_status(args) -> int:
    cfg = load_game_config(args.game)
    print(f"\n{'='*50}")
    print(f"Game:     {cfg['name']}")
    print(f"Root:     {args.game}")
    print(f"Toolkit:  {TOOLKIT}")
    print(f"Encoding: {cfg['encoding']} | Profile: {cfg['font_profile']}")
    print(f"{'='*50}")

    checks = [
        ("game/", args.game / cfg["paths"]["game_dir"]),
        ("strings/extracted.csv", args.game / cfg["files"]["extracted"]),
        ("strings/vi.csv", args.game / cfg["files"]["translated"]),
        ("strings/insured.csv", args.game / cfg["files"]["insured"]),
        ("font/atlas.png", args.game / cfg["paths"]["font_dir"] / "atlas.png"),
    ]
    for label, path in checks:
        mark = "✓" if path.exists() else "○"
        print(f"  [{mark}] {label}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Dich_game toolkit CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Toolkit: {TOOLKIT}",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Khởi tạo workspace game mới")
    p_init.add_argument("game", type=Path)
    p_init.add_argument("--encoding", default="gbk")
    p_init.add_argument("--profile", default="win95_16_composite")
    p_init.add_argument("--name")
    p_init.add_argument("--link-game", type=Path)
    p_init.set_defaults(func=cmd_init)

    for name, help_text, func in [
        ("extract", "Trích chuỗi CN/JP từ binary game", cmd_extract),
        ("build-font", "Build font VI cho game", cmd_build_font),
        ("fit", "Tối ưu chuỗi 3 tầng bảo hiểm", cmd_fit),
        ("check", "Kiểm tra tràn UI", cmd_check),
        ("status", "Xem trạng thái workspace", cmd_status),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--game", type=Path, required=True)
        p.set_defaults(func=func)

    p_pipe = sub.add_parser("pipeline", help="extract → build-font → fit")
    p_pipe.add_argument("--game", type=Path, required=True)
    p_pipe.add_argument("--with-check", action="store_true")
    p_pipe.set_defaults(func=cmd_pipeline)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
