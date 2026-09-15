from playwright.sync_api import sync_playwright
from datetime import datetime

URL = "https://centrofunzionale.regione.campania.it/"

print("Controllo del sito ufficiale della Regione Campania...")
print("Ora del controllo:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={"width": 1440, "height": 1000}
    )

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    print("Pagina caricata correttamente.")
    print("URL:", page.url)
    print("Titolo:", page.title())

    print("Attendo il caricamento dei dati...")
    page.wait_for_timeout(10000)

    testo = page.locator("body").inner_text()

    print("Dimensione testo:", len(testo))

    print("=== TESTO DELLA PAGINA ===")
    print(testo[:20000])
    print("=== FINE TESTO ===")

    with open(
        "pagina_centro_funzionale.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(testo)

    with open(
        "pagina_centro_funzionale.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(page.content())

    browser.close()

print("Controllo terminato.")
