# ระบบโพสต์ราคาทองอัตโนมัติ — ห้างทองไทยมิตร2 (อยุธยา) / ตลาดทอง

ทุกวันเวลา 09:30 น. Claude จะ:

1. อ่านราคาจาก https://www.taradthong.com/embed/?id=2
2. ตรวจตัวเลข (ถ้าผิดปกติจะไม่โพสต์ และแจ้งเจ้าของแทน)
3. สร้างการ์ดราคาทอง 1080×1080 ด้วย `render_card.py`
4. เก็บรูปไว้ในโฟลเดอร์ `images/` ของคลังนี้ (เพื่อให้ Buffer เปิดลิงก์รูปได้)
5. โพสต์ผ่าน Buffer ไปทุกช่องที่เชื่อมไว้

## ไฟล์ในคลัง

| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `render_card.py` | สร้างรูปการ์ดราคาทอง + ตรวจตัวเลข |
| `assets/logo-thaimitr2.png`, `assets/logo-taradthong.png` | โลโก้ร้าน |
| `assets/fonts/` | ฟอนต์ Kanit และ Sarabun (สัญญาอนุญาต SIL Open Font License) |
| `images/` | รูปที่โพสต์แต่ละวัน (ลบรูปเก่ากว่า 60 วันอัตโนมัติ) |

## ทดสอบสร้างรูปเอง

```bash
pip install playwright && python -m playwright install chromium
python3 render_card.py '{"date":"วันอังคารที่ 13 ตุลาคม พ.ศ.2569","time":"เวลา 09:30 น.","change":"+50","buy":"66,400","sell":"66,600","gold":"66,517","usdthb":"33.55","kitco":"4,192"}' images/test.jpg
```
