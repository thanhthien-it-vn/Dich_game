Sango II — CD-ROM (nhac hay)
============================

Game can MSCDEX + doc SANGO.WAV tu o D:. Khong mount CD se loi:
  "CD-ROM Driver not found !"

Dat MOT trong cac cach sau vao thu muc nay (CD-ROM\):

1) CUE + BIN (khuyen dung — co Redbook audio day du)
   Sango2.cue
   Sango2.bin

2) CCD + IMG
   Sango2.ccd
   Sango2.img  (hoac .sub)

3) Copy noi dung dia CD goc (fallback — nhac co the khong day du)
   SANGO.WAV, SANGO.TAB, ... (xem logs/CD_LIST.TXT)

Volume label goc: PIONEERV.01

Play:
  Play Sango2 Syllable.bat

Trong DOSBox, launch_syllable.bat tu tim:
  CD-ROM\Sango2.cue  ->  CD-ROM\Sango2.ccd  ->  mount folder CD-ROM

Duong dan host trong play_syllable.conf:
  mount c "D:\Game\VigameV1.0\games\MyRPG\game"
