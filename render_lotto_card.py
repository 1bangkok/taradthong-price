"""สร้างการ์ดผลสลากกินแบ่งรัฐบาล 1080x1080 (สไตล์เดียวกับการ์ดราคาทอง)

ใช้งาน:
    python3 render_lotto_card.py '<json>' images/lotto-2026-10-16.jpg

JSON ต้องมี:
  date    เช่น "16 ตุลาคม 2569"
  first   รางวัลที่ 1 (6 หลัก) เช่น "011781"
  near1   [2 ตัว] รางวัลข้างเคียงรางวัลที่ 1
  front3  [2 ตัว] เลขหน้า 3 ตัว
  back3   [2 ตัว] เลขท้าย 3 ตัว
  back2   เลขท้าย 2 ตัว เช่น "48"

ถ้ารูปแบบตัวเลขผิด สคริปต์จะหยุด (exit 2) และไม่สร้างรูป
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


def validate(d):
    p = []
    if not str(d.get("date", "")).strip():
        p.append("ไม่มีวันที่งวด")
    if not re.fullmatch(r"\d{6}", str(d.get("first", ""))):
        p.append(f"รางวัลที่ 1 ต้องเป็นตัวเลข 6 หลัก ({d.get('first')})")
    for key, n, digits, label in (("near1", 2, 6, "ข้างเคียงรางวัลที่ 1"),
                                  ("front3", 2, 3, "เลขหน้า 3 ตัว"),
                                  ("back3", 2, 3, "เลขท้าย 3 ตัว")):
        v = d.get(key) or []
        if len(v) != n or not all(re.fullmatch(rf"\d{{{digits}}}", str(x)) for x in v):
            p.append(f"{label} ต้องมี {n} ชุด ชุดละ {digits} หลัก ({v})")
    if not re.fullmatch(r"\d{2}", str(d.get("back2", ""))):
        p.append(f"เลขท้าย 2 ตัว ต้องเป็นตัวเลข 2 หลัก ({d.get('back2')})")
    if not p:
        f = int(d["first"])
        expect = sorted([f"{(f - 1) % 1_000_000:06d}", f"{(f + 1) % 1_000_000:06d}"])
        if sorted(d["near1"]) != expect:
            p.append(f"เลขข้างเคียง {d['near1']} ไม่ตรงกับรางวัลที่ 1 {d['first']}")
    return p


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
    near = " &nbsp;·&nbsp; ".join(d["near1"])

    def pair(nums):
        return '<span class="sep"></span>'.join(f'<span class="n3">{n}</span>' for n in nums)

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{fonts}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;overflow:hidden;font-family:'Kanit',sans-serif;color:#fff;
 background:radial-gradient(ellipse at 50% 18%,#c0282a 0%,#ac1e1e 45%,#7d1214 100%);
 display:flex;flex-direction:column;align-items:center;padding:30px 60px 36px}}
.logo{{width:370px;height:auto;display:block}}
h1{{margin-top:14px;font-size:72px;font-weight:700;line-height:1.1;
 background:linear-gradient(180deg,#fff6cf,#f2c75a 60%,#c9952f);-webkit-background-clip:text;color:transparent}}
.date{{font-family:'Sarabun','Kanit';font-size:30px;margin-top:4px;color:#fbe9c0}}
.first{{margin-top:24px;width:100%;background:#fffaf0;border-radius:26px;border:4px solid #e2b54f;
 box-shadow:0 10px 26px rgba(0,0,0,.32);text-align:center;padding:16px 16px 18px}}
.lbl{{font-size:34px;color:#9b1618;font-weight:600;line-height:1.2}}
.lbl small{{font-size:24px;color:#7d6a4a;font-weight:400}}
.big{{font-size:140px;font-weight:700;color:#2b1a0a;line-height:1.02;letter-spacing:10px}}
.near{{font-size:24px;color:#7d6a4a}}
.near b{{color:#2b1a0a;font-weight:600;letter-spacing:2px}}
.grid{{margin-top:24px;width:100%;display:grid;grid-template-columns:1fr 1fr 0.8fr;gap:18px}}
.box{{background:#fffaf0;border-radius:22px;border:3px solid #e2b54f;text-align:center;padding:18px 8px 22px;
 box-shadow:0 8px 20px rgba(0,0,0,.28);display:flex;flex-direction:column;align-items:center}}
.box .lbl{{font-size:28px}}
.row{{display:flex;gap:14px;justify-content:center;align-items:center;margin-top:8px}}
.sep{{width:3px;height:52px;background:#e2b54f;border-radius:2px}}
.n3{{font-size:66px;font-weight:700;color:#2b1a0a;line-height:1.05;letter-spacing:3px}}
.n2{{font-size:96px;font-weight:700;color:#9b1618;line-height:.95;letter-spacing:4px}}
.foot{{margin-top:auto;width:100%;display:flex;align-items:center;gap:18px}}
.tt{{width:92px;height:92px;border-radius:18px;border:3px solid #f2c75a;display:block}}
.site{{font-size:36px;font-weight:600;line-height:1.1}}
.note{{font-family:'Sarabun','Kanit';font-size:21px;color:#f3d9a8}}
</style></head><body>
<img class="logo" src="data:image/png;base64,{logo_tm}" alt="">
<h1>ผลสลากกินแบ่งรัฐบาล</h1>
<div class="date">งวดวันที่ {d['date']}</div>
<div class="first">
 <div class="lbl">รางวัลที่ 1 <small>รางวัลละ 6,000,000 บาท</small></div>
 <div class="big">{d['first']}</div>
 <div class="near">ข้างเคียงรางวัลที่ 1 &nbsp;<b>{near}</b></div>
</div>
<div class="grid">
 <div class="box"><div class="lbl">เลขหน้า 3 ตัว</div><div class="row">{pair(d['front3'])}</div></div>
 <div class="box"><div class="lbl">เลขท้าย 3 ตัว</div><div class="row">{pair(d['back3'])}</div></div>
 <div class="box"><div class="lbl">เลขท้าย 2 ตัว</div><div class="n2">{d['back2']}</div></div>
</div>
<div class="foot">
 <img class="tt" src="data:image/png;base64,{logo_tt}" alt="">
 <div><div class="site">www.taradthong.com</div><div class="note">โปรดตรวจสอบผลรางวัลอย่างเป็นทางการกับสำนักงานสลากกินแบ่งรัฐบาล (glo.or.th)</div></div>
</div>
</body></html>"""


def main():
    d = json.loads(sys.argv[1])
    out = pathlib.Path(sys.argv[2])
    problems = validate(d)
    if problems:
        print("ข้อมูลผิดปกติ ไม่สร้างรูป:", "; ".join(problems))
        sys.exit(2)
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.set_content(build_html(d), wait_until="load")
        page.evaluate("document.fonts.ready")
        if out.suffix.lower() in (".jpg", ".jpeg"):
            page.screenshot(path=str(out), type="jpeg", quality=92)
        else:
            page.screenshot(path=str(out))
        browser.close()
    print("saved", out)


if __name__ == "__main__":
    main()
