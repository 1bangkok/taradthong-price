"""สร้างการ์ดราคาทอง 1080x1080 (PNG) จากตัวเลขที่อ่านมาจากหน้า taradthong embed

ใช้งาน:
    python3 render_card.py '<json>' images/2026-10-13.png

JSON ต้องมี: date, time, change, buy, sell, gold, usdthb, kitco
เช่น {"date":"วันอังคารที่ 13 ตุลาคม พ.ศ.2569","time":"เวลา 09:30 น.","change":"+50",
      "buy":"66,400","sell":"66,600","gold":"66,517","usdthb":"33.55","kitco":"4,192"}

ถ้าตัวเลขดูผิดปกติ สคริปต์จะหยุด (exit 2) และไม่สร้างรูป เพื่อไม่ให้โพสต์ราคาผิด
"""
import base64
import json
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE / "assets" / "fonts"
THAI = "U+02D7,U+0303,U+0331,U+0E01-0E5B,U+200C-200D,U+25CC"
LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,"
         "U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")


def b64(path):
    return base64.b64encode(path.read_bytes()).decode()


def font_face(family, filename, weight):
    rng = THAI if "-thai-" in filename else LATIN
    return (f"@font-face{{font-family:'{family}';font-weight:{weight};unicode-range:{rng};"
            f"src:url(data:font/woff2;base64,{b64(FONTS / filename)}) format('woff2');}}")


def to_int(s):
    return int(re.sub(r"[^\d]", "", s))


def validate(d):
    """คืนรายการปัญหา ถ้าว่าง = ผ่าน"""
    problems = []
    for k in ("date", "time", "change", "buy", "sell", "gold", "usdthb", "kitco"):
        if not str(d.get(k, "")).strip():
            problems.append(f"ไม่มีค่า {k}")
    if problems:
        return problems
    buy, sell = to_int(d["buy"]), to_int(d["sell"])
    if not (10_000 <= buy <= 500_000 and 10_000 <= sell <= 500_000):
        problems.append(f"ราคาอยู่นอกช่วงที่เป็นไปได้ (รับซื้อ {buy}, ขายออก {sell})")
    if sell <= buy:
        problems.append(f"ขายออก ({sell}) ไม่สูงกว่ารับซื้อ ({buy})")
    if sell - buy > 1_000:
        problems.append(f"ส่วนต่างรับซื้อ-ขายออกกว้างผิดปกติ ({sell - buy} บาท)")
    if not re.fullmatch(r"[+\-]?\d[\d,]*", d["change"].strip()):
        problems.append(f"ค่าการเปลี่ยนแปลงอ่านไม่ออก ({d['change']})")
    return problems


def build_html(d):
    fonts = "".join([
        font_face("Kanit", "kanit-thai-400-normal.woff2", 400),
        font_face("Kanit", "kanit-latin-400-normal.woff2", 400),
        font_face("Kanit", "kanit-thai-600-normal.woff2", 600),
        font_face("Kanit", "kanit-latin-600-normal.woff2", 600),
        font_face("Kanit", "kanit-thai-700-normal.woff2", 700),
        font_face("Kanit", "kanit-latin-700-normal.woff2", 700),
        font_face("Sarabun", "sarabun-thai-400-normal.woff2", 400),
        font_face("Sarabun", "sarabun-latin-400-normal.woff2", 400),
    ])
    logo_tm = b64(HERE / "assets" / "logo-thaimitr2.png")
    logo_tt = b64(HERE / "assets" / "logo-taradthong.png")

    chg = d["change"].strip()
    if to_int(chg) == 0:
        chg_bg, arrow, chg_text = "#7a6a4a", "●", "ราคาเท่ารอบก่อน"
    elif chg.startswith("-"):
        chg_bg, arrow, chg_text = "#c0392b", "▼", f"{chg} บาท"
    else:
        chg_bg, arrow, chg_text = "#1f9d55", "▲", f"{chg if chg.startswith('+') else '+' + chg} บาท"

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{fonts}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;overflow:hidden;font-family:'Kanit',sans-serif;color:#fff;
 background:radial-gradient(ellipse at 50% 18%,#c0282a 0%,#ac1e1e 45%,#7d1214 100%);
 display:flex;flex-direction:column;align-items:center;padding:34px 64px 40px}}
.logo{{width:390px;height:auto;display:block}}
h1{{margin-top:16px;font-size:74px;font-weight:700;line-height:1.1;
 background:linear-gradient(180deg,#fff6cf,#f2c75a 60%,#c9952f);-webkit-background-clip:text;color:transparent}}
.date{{font-family:'Sarabun','Kanit';font-size:30px;margin-top:6px;color:#fbe9c0}}
.panel{{margin-top:34px;width:100%;display:grid;grid-template-columns:1fr 1fr;gap:24px}}
.box{{background:#fffaf0;border-radius:26px;padding:28px 16px 30px;text-align:center;
 border:4px solid #e2b54f;box-shadow:0 10px 26px rgba(0,0,0,.32)}}
.lbl{{font-size:36px;color:#9b1618;font-weight:600;line-height:1.2}}
.val{{font-size:108px;font-weight:700;color:#2b1a0a;line-height:1.05}}
.unit{{font-size:26px;color:#7d6a4a}}
.row{{margin-top:36px;display:flex;gap:14px;align-items:stretch}}
.chg{{display:flex;align-items:center;gap:10px;font-size:34px;font-weight:600;background:{chg_bg};
 padding:0 28px;border-radius:18px;white-space:nowrap}}
.chip{{border:2px solid rgba(242,199,90,.75);border-radius:16px;padding:8px 18px;font-size:22px;
 color:#fbe1a6;text-align:center;line-height:1.2}}
.chip b{{display:block;color:#fff;font-size:30px;font-weight:600}}
.foot{{margin-top:auto;width:100%;display:flex;align-items:center;gap:18px}}
.tt{{width:92px;height:92px;border-radius:18px;border:3px solid #f2c75a;display:block}}
.site{{font-size:36px;font-weight:600;line-height:1.1}}
.note{{font-family:'Sarabun','Kanit';font-size:21px;color:#f3d9a8}}
</style></head><body>
<img class="logo" src="data:image/png;base64,{logo_tm}" alt="">
<h1>ราคาทองคำแท่งวันนี้</h1>
<div class="date">{d['date']} · {d['time']}</div>
<div class="panel">
 <div class="box"><div class="lbl">รับซื้อ</div><div class="val">{d['buy']}</div><div class="unit">บาท</div></div>
 <div class="box"><div class="lbl">ขายออก</div><div class="val">{d['sell']}</div><div class="unit">บาท</div></div>
</div>
<div class="row">
 <div class="chg">{arrow} {chg_text}</div>
 <div class="chip">Gold<b>{d['gold']}</b></div>
 <div class="chip">USD/THB<b>{d['usdthb']}</b></div>
 <div class="chip">KITCO/USD<b>{d['kitco']}</b></div>
</div>
<div class="foot">
 <img class="tt" src="data:image/png;base64,{logo_tt}" alt="">
 <div><div class="site">www.taradthong.com</div><div class="note">ราคาอาจเปลี่ยนแปลงระหว่างวัน</div></div>
</div>
</body></html>"""


def main():
    d = json.loads(sys.argv[1])
    out = pathlib.Path(sys.argv[2])
    problems = validate(d)
    if problems:
        print("ตัวเลขผิดปกติ ไม่สร้างรูป:", "; ".join(problems))
        sys.exit(2)
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.set_content(build_html(d), wait_until="load")
        page.evaluate("document.fonts.ready")
        page.screenshot(path=str(out), type="jpeg", quality=92) if out.suffix.lower() in (".jpg", ".jpeg") \
            else page.screenshot(path=str(out))
        browser.close()
    print("saved", out)


if __name__ == "__main__":
    main()
