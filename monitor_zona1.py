from playwright.sync_api import sync_playwright
from datetime import datetime

URL = "https://centrofunzionale.regione.campania.it/"

print("Controllo del sito ufficiale della Regione Campania...")
print("Ora del controllo:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(URL, wait_until="networkidle", timeout=60000)

    print("Pagina caricata correttamente.")
    print("Titolo:", page.title())

    testo = page.locator("body").inner_text()

    print("=== TESTO DELLA PAGINA ===")
    print(testo[:15000])

    with open("pagina_centro_funzionale.txt", "w", encoding="utf-8") as f:
        f.write(testo)

    browser.close()

print("Controllo terminato.")
