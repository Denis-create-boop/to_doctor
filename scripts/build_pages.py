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
            p = p.rstrip("/") + "/"
        return f'{attr}="/to_doctor{p}' + (f'?{parts.query}' if parts.query else '') + (f'#{parts.fragment}' if parts.fragment else '') + '"'
    return re.sub(r'(href|src)="(/[^"]*)"',link,html)

def write(path, html):
    dest = OUT / path / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    html = rewrite(html)
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
        ids = [r["id"] for r in db().execute("SELECT id FROM doctors ORDER BY id")]
    with app.test_client() as client:
        write("", client.get("/").get_data(as_text=True))
        for slug,*_ in SPECIALTIES:
            write("specialty/"+slug,client.get("/specialty/"+slug).get_data(as_text=True))
        for doctor_id in ids:
            html = client.get(f"/book/{doctor_id}").get_data(as_text=True)
            html = re.sub(r'<input type="hidden" name="csrf"[^>]*>','',html)
            html = html.replace('<form method="post">',f'<form id="demo-booking" data-doctor="{doctor_id}">')
            html = html.replace('Время резервируется после подтверждения. Если его успеет выбрать другой посетитель, потребуется выбрать другое.','Время резервируется только в этом браузере. Другие посетители не видят ваши демонстрационные записи.')
            html = html.replace('</body>','<script src="/static/booking_demo.js"></script></body>')
            write(f"book/{doctor_id}",html)
(OUT/".nojekyll").touch()
print(f"Generated {len(ids)} booking pages")
