from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import re
import requests

# ============================================================
# CONFIGURAZIONE
# ============================================================

URL = "https://centrofunzionale.regione.campania.it/"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = "5891919449"

# ============================================================
# TELEGRAM
# ============================================================

def invia_telegram(messaggio):
    if not TELEGRAM_BOT_TOKEN:
        print("ERRORE: secret TELEGRAM_BOT_TOKEN non trovato.")
        return False

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    dati = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": messaggio
    }

    try:
        risposta = requests.post(
            url,
            data=dati,
            timeout=30
        )

        print("Telegram:", risposta.status_code)

        if risposta.ok:
            print("Messaggio Telegram inviato.")
            return True

        print("Errore Telegram:", risposta.text)
        return False

    except Exception as errore:
        print("Errore collegamento Telegram:", errore)
        return False


# ============================================================
# FUNZIONI UTILI
# ============================================================

def estrai_periodo_validita(testo):
    """
    Cerca nel testo della pagina una validità del tipo:

    Valido dalle 14:00 del 15/09/2026
    alle 14:00 del 16/09/2026
    """

    schema = re.search(
        r"Valido\s+dalle\s+(\d{1,2}:\d{2})\s+del\s+"
        r"(\d{1,2}/\d{1,2}/\d{4})\s+"
        r"alle\s+(\d{1,2}:\d{2})\s+del\s+"
        r"(\d{1,2}/\d{1,2}/\d{4})",
        testo,
        re.IGNORECASE
    )

    if schema:
        return {
            "ora_inizio": schema.group(1),
            "data_inizio": schema.group(2),
            "ora_fine": schema.group(3),
            "data_fine": schema.group(4)
        }

    return None


def stampa_elementi_zona1(page):
    """
    Cerca nella pagina elementi che potrebbero appartenere
    alla mappa delle zone di allerta.
    """

    print("")
    print("================================================")
    print("RICERCA MAPPA ZONE")
    print("================================================")

    elementi = page.locator(
        "text=/Zona\\s*1|ZONE\\s*1|ZONA\\s*1/i"
    )

    numero = elementi.count()

    print("Elementi trovati per Zona 1:", numero)

    for i in range(numero):
        try:
            elemento = elementi.nth(i)

            print("")
            print("--- ELEMENTO", i + 1, "---")

            try:
                print("Testo:", elemento.inner_text())
            except:
                print("Testo: non disponibile")

            try:
                print("Tag:", elemento.evaluate(
                    "(el) => el.tagName"
                ))
            except:
                print("Tag: non disponibile")

            try:
                print("Classe:", elemento.get_attribute("class"))
            except:
                print("Classe: non disponibile")

            try:
                print("ID:", elemento.get_attribute("id"))
            except:
                print("ID: non disponibile")

            try:
                print("Style:", elemento.get_attribute("style"))
            except:
                print("Style: non disponibile")

            try:
                print(
                    "HTML:",
                    elemento.evaluate(
                        "(el) => el.outerHTML"
                    )[:3000]
                )
            except:
                print("HTML: non disponibile")

        except Exception as errore:
            print("Errore lettura elemento:", errore)


# ============================================================
# CONTROLLO PRINCIPALE
# ============================================================

print("================================================")
print("MONITOR ALLERTA CAMPANIA - ZONA 1")
print("================================================")

print(
    "Ora del controllo:",
    datetime.now().strftime("%d/%m/%Y %H:%M:%S")
)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page(
        viewport={
            "width": 1440,
            "height": 1000
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
    print("Attendo il caricamento della mappa...")

    page.wait_for_timeout(10000)

    # ========================================================
    # TESTO PAGINA
    # ========================================================

    testo = page.locator("body").inner_text()

    print("")
    print("Dimensione testo:", len(testo))

    # ========================================================
    # PERIODO VALIDITÀ
    # ========================================================

    periodo = estrai_periodo_validita(testo)

    if periodo:

        print("")
        print("PERIODO DI VALIDITÀ TROVATO:")
        print(
            f"Dal {periodo['data_inizio']} "
            f"alle {periodo['ora_inizio']}"
        )
        print(
            f"Al {periodo['data_fine']} "
            f"alle {periodo['ora_fine']}"
        )

    else:
        print("")
        print("Periodo di validità non trovato.")

    # ========================================================
    # CERCA ZONA 1
    # ========================================================

    stampa_elementi_zona1(page)

    # ========================================================
    # SALVA PAGINA
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
