# Dich_game — Font tiếng Việt cho game DOS / Win95–98

Công cụ tạo **bitmap font atlas** tiếng Việt có dấu (UTF-8), tối ưu để việt hóa nhiều game Trung Quốc cổ.

## Tính năng chính

| Tính năng | Mô tả |
|-----------|--------|
| **Pixel-perfect** | Render upscale 4× rồi downscale NEAREST — nét chữ sắc ở 12–16px |
| **Profile game** | Preset JSON cho DOS 12×12, Win95 14px/16px — không cần nhớ tham số |
| **Cell cố định** | Khớp font monospace gốc của game (`--cell 12 12`) |
| **Export đa format** | PNG, JSON, BIN, `.fnt` (BMFont), strip DOS, `vi_glyphs.h` |
| **Runtime C** | `runtime/vi_text.c` — hook vẽ chữ UTF-8 dùng chung |
| **L10n tools** | Gom ký tự từ file dịch, kiểm tra text tràn UI |

## Quick start

```bash
pip install -r requirements.txt

# Build tất cả preset
python3 build_fonts.py

# Hoặc từng profile
python3 tools/font_atlas/generate.py --profile profiles/dos_12.json
python3 tools/font_atlas/generate.py --profile profiles/win95_16.json --preview "Nhân vật: Lý Mặc"
```

## Profile có sẵn

| Profile | Dùng cho | Cell | Ghi chú |
|---------|----------|------|---------|
| `dos_12` | DOS / VGA | 12×12 mono | 1-bit, threshold 130 |
| `win95_14` | Dialogue Win95 | proportional | 14px, không cố định cell |
| `win95_16` | Menu / UI RPG | 16×16 mono | Phổ biến nhất |
| `win95_16_bold` | Tiêu đề, skill | 16×16 mono | Font đậm |

Thêm profile mới: copy `profiles/win95_16.json`, chỉnh `size`, `cell_width/height`, `threshold`.

## Tinh chỉnh nét chữ

```bash
# Pixel sắc, cell khớp font gốc 14×14
python3 tools/font_atlas/generate.py --size 14 --render pixel --cell 14 14 --scale 4

# Smooth (anti-alias) cho game Win dùng alpha blending
python3 tools/font_atlas/generate.py --size 16 --render smooth

# DOS 1-bit: chỉnh ngưỡng nếu dấu mờ
python3 tools/font_atlas/generate.py --profile profiles/dos_12.json --threshold 120

# Căn baseline (dấu không bị cắt)
python3 tools/font_atlas/generate.py --cell 16 16 --baseline-offset 1
```

## Output mỗi lần build

| File | Dùng khi |
|------|----------|
| `atlas.png` | Sprite sheet chính |
| `atlas.json` | Metadata + metrics (variable width) |
| `atlas.bin` | Engine C/DOS đọc trực tiếp |
| `atlas.fnt` | BMFont — nhiều engine/tool hỗ trợ |
| `atlas_strip.png` | Thay tile font liên tiếp trong ROM/pak |
| `glyph_index.txt` | Tra codepoint → index strip |
| `vi_glyphs.h` | Header C kèm `runtime/vi_text.c` |
| `preview.png` | Xem nhanh câu demo |

## Quy trình việt hóa nhiều game

```
1. Phân tích game → xác định cell size (12/14/16) và encoding gốc
2. Tạo/chọn profile JSON khớp font gốc
3. Dịch text → UTF-8
4. collect_chars.py → atlas chỉ chứa ký tự cần (nhỏ, nhanh load)
5. check_strings.py → phát hiện text tràn hộp thoại
6. Patch: thay font gốc + hook vi_draw_utf8()
```

### Gom ký tự từ bản dịch (atlas nhỏ hơn)

```bash
python3 tools/l10n/collect_chars.py translations/*.csv \
  --merge tools/font_atlas/chars_vi.txt \
  -o output/chars_mygame.txt

python3 tools/font_atlas/generate.py --profile profiles/win95_16.json \
  --chars output/chars_mygame.txt --out output/mygame_font
```

### Kiểm tra text tràn UI

```bash
python3 tools/l10n/check_strings.py \
  --atlas output/win95_16/atlas.json \
  --original strings_cn.csv \
  --translated strings_vi.csv \
  --ratio 1.2
```

## Tích hợp runtime (patch DLL)

Copy `runtime/vi_text.c`, `runtime/vi_text.h` và `vi_glyphs.h` (generated) vào project patch.
Implement `ViBlitFn` theo backend game (GDI `SetPixel`, DirectDraw blit, VGA plane write).
Gọi `vi_draw_utf8()` thay `TextOut` / hàm vẽ chữ gốc.

## Tạo profile cho game mới

```json
{
  "name": "my_game",
  "size": 14,
  "render": "pixel",
  "scale": 4,
  "cell_width": 14,
  "cell_height": 14,
  "monospace": true,
  "one_bit": false,
  "chars": "chars_vi.txt",
  "out": "output/my_game",
  "notes": "Mô tả font gốc tìm được trong game"
}
```

## Lưu ý encoding

Tool dùng **UTF-8**. Game cũ có thể cần TCVN3/VNI — có thể thêm converter riêng trước bước patch binary.
