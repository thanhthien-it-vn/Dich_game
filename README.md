# Dich_game — Việt hóa game Trung / Nhật (DOS & Win95–98)

Toolkit tạo **font tiếng Việt** + xử lý **nguồn Trung (GBK) / Nhật (Shift-JIS)** cho game retro.

## Phạm vi

| Nguồn game | Encoding phổ biến | Font gốc |
|------------|-------------------|----------|
| **Trung** (99%) | GBK / GB2312 | 12×12, 16×16 fullwidth |
| **Nhật** (99%) | Shift-JIS / CP932 | 12×12, 16×16 fullwidth |
| **Đích** | UTF-8 tiếng Việt | Atlas Latin có dấu thay CJK |

Pipeline: **extract CN/JP → dịch UTF-8 → build font VI → check tràn UI → patch game**

## Tính năng chính

| Tính năng | Mô tả |
|-----------|--------|
| **Font VI pixel-perfect** | Upscale 4× NEAREST — nét sắc 12–16px |
| **Profile game** | Preset DOS 12×12, Win95 14/16px |
| **Encoding CN/JP** | GBK, Big5, Shift-JIS, CP932 ↔ UTF-8 |
| **extract_strings** | Quét binary `.exe`/`.dat` lấy chuỗi CJK |
| **check_strings** | So độ rộng: gốc CJK (fullwidth) vs bản dịch VI |
| **Export đa format** | PNG, JSON, BMFont, strip DOS, runtime C |

## Quick start

```bash
pip install -r requirements.txt
python3 build_fonts.py
```

### Game Trung (GBK)

```bash
# Trích chuỗi từ binary
python3 tools/l10n/extract_strings.py game.exe --encoding gbk -o strings_cn.csv

# Convert script
python3 tools/l10n/convert_text.py script.txt --from gbk -o script.utf8.txt

# Build font + kiểm tra tràn
python3 tools/font_atlas/generate.py --profile profiles/win95_16.json
python3 tools/l10n/check_strings.py --atlas output/win95_16/atlas.json \
  --original strings_cn.csv --translated strings_vi.csv --source gbk
```

### Game Nhật (Shift-JIS)

```bash
python3 tools/l10n/extract_strings.py game.exe --encoding shift_jis -o strings_jp.csv
python3 tools/l10n/check_strings.py --atlas output/win95_16/atlas.json \
  --original strings_jp.csv --translated strings_jp_vi.csv --source shift_jis
```

## Khác biệt Trung vs Nhật (khi việt hóa)

| | Trung (GBK) | Nhật (Shift-JIS) |
|---|-------------|------------------|
| Ký tự gốc | Hán giản/thể | Kanji + Hiragana + Katakana |
| Bytes/char | 2 (hầu hết) | 1–2 (halfwidth/fullwidth) |
| Font cell | Thường 16×16 | Thường 16×16 (DOS: 12×12) |
| Tool extract | `--encoding gbk` | `--encoding shift_jis` |
| Tên riêng | Giữ Hán hoặc phiên âm | Giữ romaji/kanji tùy game |

**Lưu ý:** Bản dịch tiếng Việt **dài hơn nhiều** so với CJK cùng nghĩa — `check_strings --ratio 1.2` thường vẫn báo tràn; cần rút gọn câu hoặc nới UI.

## Profile font

| Profile | Game | Cell |
|---------|------|------|
| `dos_12` | DOS CN/JP compact | 12×12 |
| `win95_16` | RPG Win95 CN/JP | 16×16 |
| `win95_14` | Dialogue proportional | ~14px |
| `win95_16_bold` | Tiêu đề | 16×16 bold |

## Output mỗi lần build

`atlas.png`, `atlas.json`, `atlas.bin`, `atlas.fnt`, `atlas_strip.png`, `vi_glyphs.h`, `preview.png`

## Quy trình đầy đủ

```
1. Xác định nguồn: CN (gbk) hay JP (shift_jis)
2. extract_strings → CSV
3. Dịch sang UTF-8 tiếng Việt
4. collect_chars → atlas tối thiểu
5. generate font (profile khớp cell game)
6. check_strings (gốc CJK fullwidth vs VI)
7. Patch binary + hook vi_draw_utf8()
```

## Runtime patch

Copy `runtime/vi_text.c` + `vi_glyphs.h` vào project patch. Implement blit theo backend game.

## Encoding legacy VN

Tool dùng UTF-8. TCVN3/VNI có thể thêm converter nếu cần cho tool dịch cũ.
