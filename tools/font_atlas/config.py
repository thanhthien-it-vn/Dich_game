"""Load profile JSON cho từng loại game."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any


@dataclass
class FontConfig:
    name: str = "custom"
    font: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    size: int = 16
    bold: bool = False
    padding: int = 1
    cols: int = 16
    render: str = "pixel"  # pixel | smooth
    scale: int = 4  # upscale khi render pixel
    one_bit: bool = False
    threshold: int = 140
    cell_width: int | None = None
    cell_height: int | None = None
    monospace: bool = False
    baseline_offset: int = 0
    export_bmfont: bool = True
    export_strip: bool = True
    chars: str = "chars_vi.txt"
    out: str = "output/font_16"
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FontConfig:
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    def resolve_paths(self, base: Path) -> FontConfig:
        cfg = FontConfig(**{f.name: getattr(self, f.name) for f in fields(self)})
        if not Path(cfg.font).is_absolute():
            cfg.font = str((base / cfg.font).resolve())
        if not Path(cfg.chars).is_absolute():
            cfg.chars = str((base / cfg.chars).resolve())
        if not Path(cfg.out).is_absolute():
            cfg.out = str((base.parent.parent / cfg.out).resolve())
        return cfg


def load_profile(path: Path) -> FontConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    return FontConfig.from_dict(data)
