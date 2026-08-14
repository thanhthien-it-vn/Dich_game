"""Big5 2-byte slot iterator cho Sango II / game Big5 DOS."""

from __future__ import annotations


def iter_big5_slots(start_lead: int = 0xA3, start_trail: int = 0xBF):
    """Vùng Big5 ít dùng — gán tiếng Việt syllable (tương tự GBK B0A1)."""
    lead, trail = start_lead, start_trail
    while lead <= 0xF9:
        while trail <= 0xFE:
            if trail != 0x7F:
                yield lead, trail
            trail += 1
        trail = 0x40
        lead += 1


def assign_big5_codes(syllables: list[str], start_lead: int = 0xA3, start_trail: int = 0xBF) -> dict[str, tuple[int, int]]:
    slots = iter_big5_slots(start_lead, start_trail)
    mapping: dict[str, tuple[int, int]] = {}
    for syl in syllables:
        lead, trail = next(slots)
        mapping[syl] = (lead, trail)
    return mapping


def big5_to_glyph_index(lead: int, trail: int) -> int:
    """Công thức Big5 → index glyph phổ biến DOS (13354 slot FONT16.PAT)."""
    if trail >= 0xA1:
        return (lead - 0xA1) * 157 + (trail - 0xA1) + 63
    return (lead - 0xA1) * 157 + (trail - 0x40)
