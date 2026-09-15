from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import re
import requests

URL = "https://centrofunzionale.regione.campania.it/"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = "5891919449"


def invia_telegram(messaggio):
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN non trovato.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        risposta = requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": messaggio
            },
            timeout=30
        )

        print("Telegram:", risposta.status_code)
        print(risposta.text)

        return risposta.ok

    except Exception as errore:
        print("Errore Telegram:", errore)
        return False


def estrai_periodo_validita(testo):
    risultato = re.search(
        r"Valido\s+dalle\s+(\d{1,2}:\d{2})\s+del\s+"
        r"(\d{1,2}/\d{1,2}/\d{4})\s+"
        r"alle\s+(\d{1,2}:\d{2})\s+del\s+"
        r"(\d{1,2}/\d{1,2}/\d{4})",
        testo,
        re.IGNORECASE
    )

    if not risultato:
        return None

    return {
        "ora_inizio": risultato.group(1),
        "data_inizio": risultato.group(2),
        "ora_fine": risultato.group(3),
        "data_fine": risultato.group(4)
    }


print("================================================")
print("MONITOR ALLERTA CAMPANIA - ZONA 1")
print("================================================")

print(
    "Ora controllo:",
    datetime.now().strftime("%d/%m/%Y %H:%M:%S")
)

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={
            "width": 1440,
            "height": 1200
        }
    )

    print("")
    print("Apro il sito ufficiale...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    print("Pagina caricata.")
    print("URL:", page.url)
    print("Titolo:", page.title())

    print("")
    print("Attendo il caricamento completo...")
    page.wait_for_timeout(10000)

    # ========================================================
    # TESTO
    # ========================================================

    testo = page.locator("body").inner_text()

    periodo = estrai_periodo_validita(testo)

    print("")
    print("================================================")
    print("PERIODO DI VALIDITÀ")
    print("================================================")

    if periodo:
        print(
            "Inizio:",
            periodo["data_inizio"],
            periodo["ora_inizio"]
        )

        print(
            "Fine:",
            periodo["data_fine"],
            periodo["ora_fine"]
        )
    else:
        print("Periodo non trovato.")

    # ========================================================
    # ELEMENTI SVG
    # ========================================================

    print("")
    print("================================================")
    print("ANALISI SVG / MAPPA")
    print("================================================")

    svg_count = page.locator("svg").count()

    print("SVG trovati:", svg_count)

    for i in range(svg_count):

        svg = page.locator("svg").nth(i)

        try:
            box = svg.bounding_box()

            print("")
            print("----- SVG", i + 1, "-----")

            print("Posizione:", box)

            print(
                "HTML:",
                svg.evaluate(
                    "(el) => el.outerHTML"
                )[:5000]
            )

        except Exception as errore:

            print(
                "Errore SVG:",
                errore
            )

    # ========================================================
    # ELEMENTI CON COLORE
    # ========================================================

    print("")
    print("================================================")
    print("ANALISI ELEMENTI COLORATI")
    print("================================================")

    elementi = page.locator(
        "[style], [fill], [class]"
    )

    totale = elementi.count()

    print(
        "Elementi analizzati:",
        totale
    )

    trovati = 0

    for i in range(min(totale, 1000)):

        elemento = elementi.nth(i)

        try:

            style = elemento.get_attribute("style")
            fill = elemento.get_attribute("fill")
            classe = elemento.get_attribute("class")

            valori = " ".join(
                str(x)
                for x in [
                    style,
                    fill,
                    classe
                ]
                if x
            ).lower()

            colori = [
                "green",
                "lime",
                "yellow",
                "orange",
                "red",
                "rgb",
                "#"
            ]

            if any(
                colore in valori
                for colore in colori
            ):

                trovati += 1

                print("")
                print("ELEMENTO COLORATO", trovati)

                print("Tag:", elemento.evaluate(
                    "(el) => el.tagName"
                ))

                print("Classe:", classe)
                print("Fill:", fill)
                print("Style:", style)

                try:
                    print(
                        "Testo:",
                        elemento.inner_text()
                    )
                except:
                    pass

                if trovati >= 100:
                    break

        except:
            pass

    print("")
    print(
        "Elementi colorati trovati:",
        trovati
    )

    # ========================================================
    # SCREENSHOT DELLA PAGINA
    # ========================================================

    print("")
    print("Salvo screenshot della pagina...")

    page.screenshot(
        path="pagina_centro_funzionale.png",
        full_page=True
    )

    # ========================================================
    # SALVATAGGIO
    # ========================================================

    with open(
        "pagina_centro_funzionale.txt",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(testo)

    with open(
        "pagina_centro_funzionale.html",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(page.content())

    browser.close()

print("")
print("================================================")
print("CONTROLLO TERMINATO")
print("================================================")
