# Dich_game — Font tiếng Việt cho game DOS / Win95–98

Công cụ tạo **bitmap font atlas** tiếng Việt có dấu (UTF-8), dùng chung khi dịch nhiều game Trung Quốc cổ.

## Vấn đề

Game DOS / Win95–98 tiếng Trung thường:

- Dùng font bitmap GB2312/GBK (12×12, 14×14, 16×16…)
- Không có sẵn ký tự tiếng Việt có dấu
- Engine vẽ chữ qua hàm riêng (GDI, DirectDraw, VGA text mode, custom blit)

**Giải pháp:** thay / hook font gốc bằng atlas tiếng Việt + bảng tra glyph, patch chuỗi dịch UTF-8.

## Tạo atlas

```bash
# Font 16px (phổ biến RPG Win95)
python3 tools/font_atlas/generate.py --size 16

# Font 12px + 1-bit cho DOS/VGA
python3 tools/font_atlas/generate.py --size 12 --1bit --out output/font_12

# Font TTF tùy chọn
python3 tools/font_atlas/generate.py --font /path/to/font.ttf --size 14
```

Kết quả trong `output/font_16/`:

| File | Mô tả |
|------|--------|
| `atlas.png` | Sprite sheet (RGBA) |
| `atlas.json` | Vị trí + metrics từng ký tự |
| `atlas.bin` | Pack binary cho engine C |
| `vi_glyphs.h` | Header tra cứu theo codepoint |

## Tích hợp vào game

1. **Phân tích game** — tìm file `.fon`, `.fnt`, tile font trong `.pak`, hoặc hàm `TextOut` / `DrawText`.
2. **Khớp kích thước** — `--size` trùng cell font gốc (thường 12/14/16).
3. **Patch chuỗi** — thay text GBK bằng UTF-8 trong file script / binary.
4. **Hook vẽ chữ** — đọc UTF-8, tra `atlas.json` / `vi_glyphs.h`, blit từ `atlas.png`.

## Bộ ký tự

Chỉnh `tools/font_atlas/chars_vi.txt` để thêm/bớt ký tự (mặc định: Latin + đủ dấu tiếng Việt).

## Lưu ý encoding cũ

Một số tool dịch cũ dùng TCVN3 / VNI / VISCII. Tool này dùng **UTF-8** (chuẩn hiện đại). Có thể thêm converter nếu game yêu cầu code page cụ thể.
