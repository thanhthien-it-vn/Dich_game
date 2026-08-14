# Sango II — Syllable có dấu (VigameV1.0)

Tam Quốc Chí 2 DOS, encoding **Big5**, 1 tiếng Việt = 1 ô = 2 byte (như chữ Hán).

## Pipeline

```powershell
cd D:\Game\VigameV1.0

# Extract JSON repo → vi.csv + build font + encode
python dich.py sango2 --game D:\Game\VigameV1.0\games\MyRPG

# Thêm patch font + EXE
python dich.py sango2 --game games\MyRPG --patch-font --patch-exe
```

## Output

| File | Mô tả |
|------|--------|
| `games/MyRPG/strings/vi.csv` | 1624 chuỗi (từ repo JSON) |
| `games/MyRPG/font/atlas.png` | 906 tiếng có dấu |
| `games/MyRPG/font/syllable_map.json` | Map Big5 A3BF… |
| `games/MyRPG/game/SANGO2/FONT16-SYLLABLE.PAT` | Font 16px |
| `games/MyRPG/patch/SAN2-SYLLABLE.EXE` | EXE đã patch |

## Chơi thử (Windows + DOSBox)

1. Copy `FONT16-SYLLABLE.PAT` → `FONT16-VN.PAT` (backup gốc trước)
2. Copy `patch/SAN2-SYLLABLE.EXE` → `SANGO2/SAN2-VN.EXE`
3. Chạy `Play Sango2 VN.bat`

## Thống kê patch (lần chạy đầu)

- **1334** chuỗi patched có dấu
- **117** overflow (câu dài hơn slot Hán — cần fit syllable)
- **173** skipped (vùng menu / không khớp offset)

## Fit overflow

Chuỗi overflow: tiếng Việt nhiều hơn số ô Hán gốc → chạy fit 3 tầng rồi patch lại (TODO: `fit_syllable` tích hợp).

## Khác repo cũ (không dấu)

| | repo cũ | Vigame syllable |
|---|---------|-----------------|
| In-game | ASCII không dấu | **Có dấu** |
| Font | Latin ASCII slot | Syllable atlas Big5 |
| Encode | abbrev | syllable_map Big5 |
