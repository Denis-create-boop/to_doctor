from pathlib import Path
import os, subprocess, sys, time
from playwright.sync_api import sync_playwright
root=Path("site").resolve()
mount=Path("/tmp/medika-pages-test")
mount.mkdir(exist_ok=True)
link=mount/"to_doctor"
if not link.exists(): link.symlink_to(root,target_is_directory=True)
server=subprocess.Popen([sys.executable,"-m","http.server","8765","--directory",str(mount)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    time.sleep(1)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        page=browser.new_page()
        page.goto("http://127.0.0.1:8765/to_doctor/")
        page.locator(".specialty").first.click()
        page.locator(".doctor-card .button").first.click()
        page.locator(".date-grid .day").nth(2).click()
        page.locator('input[name="visit_time"]:not([disabled])').first.check()
        page.locator('input[name="patient_name"]').fill("Учебный Пациент")
        snils=page.locator('input[name="snils"]')
        snils.fill("145")
        assert page.locator(".snils-mask-guide").inner_text()=="145-000-000-00"
        assert page.locator(".snils-mask-guide .snils-entered").inner_text()=="145-"
        assert snils.input_value()=="145"
        snils.fill("00000000000")
        snils.press("End")
        snils.press("9")
        assert page.locator(".snils-mask-guide").inner_text()=="000-000-000-00"
        assert page.locator('input[name="snils"]').input_value()=="000-000-000-00"
        page.locator('input[name="birth_date"]').fill("2000-01-01")
        day=page.locator('input[name="day"]').input_value()
        slot=page.locator('input[name="visit_time"]:checked').input_value()
        page.locator("#demo-booking button[type=submit]").click()
        page.locator("dialog[open]").wait_for(timeout=10000)
        page.get_by_role("button",name="Посмотреть запись").click()
        page.locator("#receipt-title").get_by_text("Вы записаны на приём!").wait_for(timeout=10000) if False else page.wait_for_function("document.querySelector('#receipt-title')?.textContent === 'Вы записаны на приём!'")
        assert page.locator("#receipt-date").inner_text()==".".join(reversed(day.split("-")))
        assert page.locator("#receipt-time").inner_text()==slot
        page.reload()
        page.wait_for_function("document.querySelector('#receipt-title')?.textContent === 'Вы записаны на приём!'")
        browser.close()
finally:
    server.terminate()
