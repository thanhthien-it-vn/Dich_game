# Dich_game — Việt hóa game Trung / Nhật (DOS & Win95–98)

**Toolkit đóng gói** — 1 thư mục cố định, mỗi game 1 workspace riêng.

→ **Cách dùng Cursor Cloud:** xem [CURSOR.md](CURSOR.md)

```bash
pip install -r requirements.txt
python3 dich.py init ~/games/MyRPG --encoding gbk
python3 dich.py pipeline --game ~/games/MyRPG
```

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

### Công nghệ: Việt hóa CÓ DẤU (mục tiêu vô cực)

### Vấn đề gốc

Game CJK dùng cell **16×16 fullwidth**. Tiếng Việt Latin có dấu **cao hơn** → dấu bị cắt nếu render TTF thuần.

### Giải pháp đã tích hợp

| Lớp | Công nghệ | Mục đích |
|-----|-----------|----------|
| **Composite glyph** | Unicode NFD + vùng dấu 28% / thân 72% | Dấu sắc/huyền/hỏi/ngã/nặng trong 12×12, 16×16 |
| **FreeType autohint** | `freetype-py` FT_LOAD_TARGET_MONO | Nét pixel sắc như font game gốc |
| **fonttools** | Subset, metrics, export | Pipeline font chuyên nghiệp |
| **uharfbuzz** | HarfBuzz shaping | Sẵn sàng cho mix Hán-Việt |
| **smart_fit** | Paraphrase **giữ dấu** | Rút câu không bỏ thanh điệu |
| **fit_text** | Viết tắt + bỏ dấu (fallback) | UI cực chật |

### Build font composite (CÓ DẤU)

```bash
pip install -r requirements.txt

# Win95 16×16 — FreeType composite
python3 tools/font_atlas/generate.py --profile profiles/win95_16_composite.json

# DOS 12×12 1-bit composite
python3 tools/font_atlas/generate.py --profile profiles/dos_12_composite.json
```

### Smart fit — rút câu GIỮ DẤU

```bash
# Không bao giờ bỏ dấu — chỉ paraphrase
python3 tools/l10n/smart_fit_cli.py "Chào mừng đến với trò chơi" \
  --max-width 96 --atlas output/win95_16/atlas.json
# → Chào! (80px, có dấu)

python3 tools/l10n/smart_fit_cli.py --csv strings_vi.csv --original strings_cn.csv \
  --atlas output/win95_16/atlas.json -o strings_vi_smart.csv
```

Rules: `tools/l10n/paraphrase_rules.json` (exact, synonyms, patterns)

### Hướng R&D tiếp (stack đồ sộ)

| Công nghệ | Ứng dụng |
|-----------|----------|
| **msdf-atlas-gen** | Font scale mượt game Win98+ / OpenGL |
| **rectpack** | Atlas variable-width tiết kiệm VRAM |
| **OpenCV morphology** | Cleanup 1-bit DOS |
| **LLM constrained decode** | Paraphrase có dấu theo pixel budget |
| **Neural bitmap font** | Train 12×12 VN glyph giống font game gốc |
| **Patch UI engine** | Nới hộp thoại + word-wrap thay rút câu |

### Pipeline 3 tầng bảo hiểm (khuyến nghị)

```
T1  CÓ DẤU          → paraphrase ("Chào!")
T2  Viết tắt có dấu → N.vật, Ch.mừng
T3  Bảo hiểm        → HP/MP/EXP + VI không dấu  ← tầng fallback
```

Tự động thử T1 → T2 → T3 cho đến khi vừa pixel:

```bash
python3 tools/l10n/fit_insurance_cli.py "Chào mừng đến với trò chơi" \
  --max-width 96 --atlas output/win95_16/atlas.json

python3 tools/l10n/fit_insurance_cli.py "Sinh mạng và năng lượng còn đầy" \
  --max-width 160 --atlas output/win95_16/atlas.json --show-tiers

python3 tools/l10n/fit_insurance_cli.py --csv strings_vi.csv --original strings_cn.csv \
  --atlas output/win95_16/atlas.json -o strings_insured.csv
```

Config: `tools/l10n/insurance_tiers.json` (english_terms, tier3_phrases)

| Tầng | Khi dùng | Ví dụ |
|------|----------|-------|
| **T1** | UI đủ rộng | `Chào!`, `Bắt đầu` |
| **T2** | Hơi chật | `N.vật`, `Chơi` |
| **T3** | Cực chật / stat | `HP MP full`, `Chao!` |

### Pipeline đầy đu cho CÓ DẤU

```
1. Font composite (FreeType) → dấu trong cell
2. smart_fit → rút câu giữ dấu
3. Nếu vẫn tràn → patch UI (nới box) HOẶC fit_text (bỏ dấu — cuối cùng)
```

## Tối ưu chuỗi dịch (viết tắt / bỏ dấu — fallback)

```bash
# Một câu — giới hạn 96px (6 ký tự CJK gốc × 16px)
python3 tools/l10n/fit_text.py "Chào mừng đến với trò chơi" \
  --max-width 96 --atlas output/win95_16/atlas.json

# Xem mọi biến thể
python3 tools/l10n/fit_text.py "Chào mừng đến với trò chơi" \
  --max-width 96 --atlas output/win95_16/atlas.json --show-all

# Hàng loạt — max-width tự tính từ bản gốc CJK
python3 tools/l10n/fit_text.py --csv strings_vi.csv --original strings_cn.csv \
  --atlas output/win95_16/atlas.json -o strings_vi_fitted.csv

# Cấm bỏ dấu (chỉ viết tắt)
python3 tools/l10n/fit_text.py "..." --max-width 96 --atlas ... --no-diacritics
```

Thứ tự ưu tiên: **giữ dấu** → viết tắt từ điển → siêu ngắn (`abbrev_rules.json`) → cắt từ → không dấu.

Sửa rules tại `tools/l10n/abbrev_rules.json` (phrases, ultra_short, drop_words).

## Runtime patch

Copy `runtime/vi_text.c` + `vi_glyphs.h` vào project patch. Implement blit theo backend game.

## Encoding legacy VN

Tool dùng UTF-8. TCVN3/VNI có thể thêm converter nếu cần cho tool dịch cũ.
