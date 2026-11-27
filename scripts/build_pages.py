"""Build a static, browser-only demo. Never export the clinic database."""
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
import re
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site"
os.environ["SECRET_KEY"] = "static-build-unused-session-key"
from main import app, SPECIALTIES, db, init_db, SLOTS

def rewrite(html):
    def link(match):
        attr, path = match.groups()
        if path.startswith("//"):
            return match.group(0)
        parts = urlsplit(path)
        p = parts.path
        if not p.startswith("/static/"):
            # Flask url_for chooses the short /<slug> route; Pages uses explicit specialty directories.
            if p.strip("/") in {spec[0] for spec in SPECIALTIES}:
                p = "/specialty/" + p.strip("/")
            p = p.rstrip("/") + "/"
        return f'{attr}="/to_doctor{p}' + (f'?{parts.query}' if parts.query else '') + (f'#{parts.fragment}' if parts.fragment else '') + '"'
    return re.sub(r'(href|src)="(/[^"]*)"',link,html)

def write(path, html):
    dest = OUT / path / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    html = rewrite(html)
    html = html.replace('</nav>', '<a href="/to_doctor/confirmation/">Моя запись</a></nav>')
    notice = '<div style="padding:12px;text-align:center;background:#fff2ce;color:#54400c">Демонстрация GitHub Pages. Записи сохраняются только в этом браузере. Используйте вымышленные данные.</div>'
    dest.write_text(html.replace("<main>", notice+"<main>"),encoding="utf-8")

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(ROOT/"static",OUT/"static")
shutil.copyfile(ROOT/"scripts"/"booking_demo.js",OUT/"static"/"booking_demo.js")
with TemporaryDirectory() as tmp:
    app.config["DATABASE"] = str(Path(tmp)/"demo.sqlite3")
    with app.app_context():
        init_db()
        doctors = [dict(r) for r in db().execute("SELECT id,name,specialty FROM doctors ORDER BY id")]
        ids = [r["id"] for r in doctors]
    with app.test_client() as client:
        write("", client.get("/").get_data(as_text=True))
        for slug,*_ in SPECIALTIES:
            write("specialty/"+slug,client.get("/specialty/"+slug).get_data(as_text=True))
        for doctor_id in ids:
            html = client.get(f"/book/{doctor_id}").get_data(as_text=True)
            html = re.sub(r'<input type="hidden" name="csrf"[^>]*>','',html)
            html = html.replace('<form method="post">',f'<form id="demo-booking" method="post" data-doctor="{doctor_id}">')
            html = re.sub(r' pattern="[^"]+"', '', html)
            html = html.replace('<button class="button"', '<button class="button" type="submit"')
            html = html.replace('Время резервируется после подтверждения. Если его успеет выбрать другой посетитель, потребуется выбрать другое.','Время резервируется только в этом браузере. Другие посетители не видят ваши демонстрационные записи.')
            html = html.replace('</body>','<script src="/static/booking_demo.js"></script></body>')
            write(f"book/{doctor_id}",html)
# Build an explicit receipt page from the existing Flask layout.
import json
from flask import render_template
with app.test_request_context("/confirmation"):
    html=render_template("confirmation_demo.html")
    write("confirmation",html)
roles={spec[0]:spec[2] for spec in SPECIALTIES}
(OUT/"static"/"demo_doctors.json").write_text(json.dumps({str(d["id"]):{"name":d["name"],"specialty":roles[d["specialty"]]} for d in doctors},ensure_ascii=False),encoding="utf-8")
shutil.copyfile(ROOT/"scripts"/"confirmation_demo.js",OUT/"static"/"confirmation_demo.js")
(OUT/".nojekyll").touch()
print(f"Generated {len(ids)} booking pages")

# Fail the build if any generated internal navigation points to a missing page.
from html.parser import HTMLParser
class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths=[]
    def handle_starttag(self, tag, attrs):
        for key,value in attrs:
            if key in ("href","src") and value and value.startswith("/to_doctor/"):
                self.paths.append(urlsplit(value).path.removeprefix("/to_doctor/"))
for page in OUT.rglob("*.html"):
    parser=Links()
    parser.feed(page.read_text(encoding="utf-8"))
    for path in parser.paths:
        target=OUT/path
        if target.is_dir(): target=target/"index.html"
        if not target.is_file():
            raise RuntimeError(f"Broken link in {page}: {path}")
print("All internal links verified")
