Sango II — CD-ROM (CloneCD)
============================

## 3 file nay la gi?

Ban convert tu **dia CD vat ly** bang **CloneCD** (phan mem rip CD pho bien
thoi DOS/Win98). Day KHONG phai 3 dia — ma la **1 dia ao** tach thanh 3 phan:

| File | Vai tro | Kich thuoc |
|------|---------|------------|
| `Sango2.ccd` | Bang track / TOC (metadata) | ~5 KB |
| `Sango2.img` | Anh raw toan bo sector (data + nhac) | ~611 MB |
| `Sango2.sub` | Subchannel (96 byte/frame) | ~25 MB |

**Dia goc ngay xua:** CD-ROM vat ly (Mixed Mode)
- **Track 1 — DATA:** 11 game + thu muc `CRACK/` + `SANGO.WAV` (~25 MB)
- **Track 2–25 — AUDIO Redbook:** nhac nen (~24 bai)

Vi sao rut dia CD la mat nhac? Game doc nhac tu **track audio tren CD**,
khong phai file WAV tren o cung (du co SANGO.WAV tren data track, nhac hay
van can CD mount de phat Redbook).

Volume label: `PIONEERV01`

---

## Hoan nguyen thanh 1 dia (ao)

3 file `.ccd + .img + .sub` **da la 1 dia day du**. Khong can gop lai.

De dung voi DOSBox-X (co nhac):

```
Sango2.cue   ← da tao san, tro vao Sango2.img
Sango2.img
```

Trong DOSBox:
```
imgmount d C:\CD-ROM\Sango2.cue -t cdrom
```

Tao lai CUE neu can:
```powershell
python dich.py sango2-cd --game games\MyRPG cue
```

---

## Phan tich / boc tach

```powershell
cd D:\Game\VigameV1.0

# Xem cau truc 25 track + thu muc tren dia
python dich.py sango2-cd --game games\MyRPG analyze

# Extract thu muc CRACK (copy vao SANGO2 sau cai dat)
python dich.py sango2-cd --game games\MyRPG extract --only crack -o games\MyRPG\game\_crack

# Extract file data Sango2 (khong can track audio)
python dich.py sango2-cd --game games\MyRPG extract --only sango2-data -o games\MyRPG\game\_cd_data

# Extract toan bo track DATA (~359 MB)
python dich.py sango2-cd --game games\MyRPG extract --only all -o D:\temp\cd_extract
```

---

## Choi game co nhac

```
Play Sango2 Syllable.bat
```

Script tu mount `Sango2.cue` (uu tien) hoac `Sango2.ccd`.

**Git LFS:** `.img` va `.sub` lon — can `git lfs pull` sau khi clone.
