import urllib.request
from datetime import datetime

URL = "https://centrofunzionale.regione.campania.it/"

print("Controllo del sito ufficiale della Regione Campania...")
print("Ora del controllo:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

request = urllib.request.Request(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

with urllib.request.urlopen(request, timeout=30) as response:
    html = response.read().decode("utf-8", errors="ignore")

print("Sito raggiunto correttamente.")
print("Dimensione pagina:", len(html), "caratteri")

with open("pagina_centro_funzionale.html", "w", encoding="utf-8") as file:
    file.write(html)

print("Pagina salvata nel file pagina_centro_funzionale.html")
