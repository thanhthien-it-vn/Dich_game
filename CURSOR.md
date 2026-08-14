# Cách dùng với Cursor Cloud

Đây là **toolkit đóng gói** — bạn giữ 1 thư mục `Dich_game`, mỗi game cần dịch có **1 workspace riêng**.

## Mô hình 2 thư mục

```
~/tools/Dich_game/              ← toolkit (repo này) — cố định
~/games/MyRPG/                  ← workspace dịch từng game
~/games/AnotherGame/
```

**Cursor Cloud:** chỉ agent vào **toolkit** + **thư mục game** cần dịch.

---

## Bước 1 — Khởi tạo game mới (1 lần)

```bash
cd ~/tools/Dich_game
pip install -r requirements.txt

# Trung (GBK)
python3 dich.py init ~/games/MyRPG --encoding gbk --profile win95_16_composite

# Nhật (Shift-JIS)
python3 dich.py init ~/games/Slayers --encoding shift_jis --profile dos_12_composite

# Symlink file game gốc
python3 dich.py init ~/games/MyRPG --link-game "/path/to/game/files"
```

Tạo ra:

```
MyRPG/
├── dich.game.json
├── game/           ← file .exe .dat gốc
├── strings/        ← CSV chuỗi
├── font/           ← font VI output
├── patch/          ← patch output
└── notes/
```

---

## Bước 2 — Cursor Cloud

Mở agent, nói ví dụ:

> Dùng toolkit `~/tools/Dich_game` để dịch game tại `~/games/MyRPG`.
> Encoding GBK, profile win95_16_composite.

Agent đọc `.cursor/rules/dich-game-toolkit.mdc` và chạy pipeline.

---

## Bước 3 — Pipeline

```bash
# Trích chuỗi
python3 dich.py extract --game ~/games/MyRPG

# (Dịch strings/vi.csv — tay hoặc agent)

# Build font + fit 3 tầng
python3 dich.py build-font --game ~/games/MyRPG
python3 dich.py fit --game ~/games/MyRPG

# Xem trạng thái
python3 dich.py status --game ~/games/MyRPG

# Gộp (khi vi.csv đã có)
python3 dich.py pipeline --game ~/games/MyRPG
```

---

## dich.game.json (config từng game)

```json
{
  "name": "MyRPG",
  "encoding": "gbk",
  "font_profile": "win95_16_composite",
  "cell_width": 16,
  "cell_height": 16
}
```

Sửa khi biết font gốc game (12×12, 16×16…).

---

## Copy toolkit sang máy khác

Chỉ cần copy **cả thư mục** `Dich_game/`:

```
Dich_game/
├── dich.py              ← CLI chính
├── build_fonts.py
├── requirements.txt
├── tools/
├── profiles/
├── runtime/
├── templates/
├── scripts/
└── .cursor/rules/       ← agent biết cách làm
```

Không cần cài đặt phức tạp: `pip install -r requirements.txt`.

---

## Checklist nghiệm thu toolkit

- [x] 1 thư mục portable
- [x] CLI `dich.py` entry point
- [x] Workspace template per game
- [x] Cursor rules cho Cloud Agent
- [x] Pipeline extract → dịch → font → fit

Phase tiếp: patch game cụ thể vào `patch/` (agent làm theo từng game).
