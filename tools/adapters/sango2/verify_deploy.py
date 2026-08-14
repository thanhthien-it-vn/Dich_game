#!/usr/bin/env python3
"""Kiem tra deploy Sango2 syllable — PAT glyph 982 (Tao) da patch chua."""

from __future__ import annotations

import sys
from pathlib import Path

GAME = Path(__file__).resolve().parents[1] / "game" / "SANGO2"


def main() -> int:
    pat = GAME / "FONT16.PAT"
    pat_s = GAME / "FONT16-SYLLABLE.PAT"
    exe = GAME / "SAN2-VN.EXE"
    exe_p = Path(__file__).resolve().parents[1] / "patch" / "SAN2-SYLLABLE.EXE"

    ok = True
    if not pat_s.exists():
        print("FAIL: thieu FONT16-SYLLABLE.PAT — chay pipeline")
        return 1

    if pat.exists():
        a = pat.read_bytes()
        b = pat_s.read_bytes()
        if a == b:
            print("OK: FONT16.PAT = SYLLABLE")
        else:
            print("WARN: FONT16.PAT KHAC FONT16-SYLLABLE.PAT — chay Deploy Syllable.bat")
            ok = False
    else:
        print("WARN: chua co FONT16.PAT")
        ok = False

    # Glyph 982 = Big5 A768 (Tao)
    idx = 982
    if pat_s[idx * 32 : (idx + 1) * 32] != Path(GAME / "FONT16.PAT").read_bytes()[idx * 32 : (idx + 1) * 32] if pat.exists() else b"\xff":
        print(f"OK: glyph slot {idx} da co syllable trong SYLLABLE.PAT")
    orig = Path(GAME / "FONT16.PAT").read_bytes() if (GAME / "FONT16.PAT").exists() else None
    if orig and pat_s[982 * 32 : 983 * 32] == orig[982 * 32 : 983 * 32]:
        print("FAIL: glyph 982 chua thay doi — pipeline loi")
        ok = False

    if exe_p.exists() and exe.exists():
        if exe.read_bytes() == exe_p.read_bytes():
            print("OK: SAN2-VN.EXE = patch syllable")
        else:
            print("WARN: SAN2-VN.EXE chua copy tu patch — chay Deploy Syllable.bat")
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
