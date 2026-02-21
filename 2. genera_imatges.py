# Importem les llibreries necessàries
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Script que donats ids de les xapes, extreu les imatges de xapes.net d'aquells ids i les guarda en una carpeta local

# URL d'on itera les imatges
BASE = "https://www.xapes.net/ca/xapa/{}/caves"
# directori local on guardem les imatges
OUTPUT_DIR = "imatges_xapes"
# Llista d'IDs de xapes a extrure-li la fotografia
NUMEROS = [3508	,
50637	,
35642	,
338
]
# retard entre peticions
DELAY_SECONDS = 0.2
# headers necessaris pels request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ImageDownloader/1.0; +https://example.com/)"
}
# tipus d'imatge a extreure
ALLOWED_EXTS = (".jpg", ".jpeg")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_valid_image_url(url: str) -> bool:
    """Comprova si l'URL sembla una imatge pel seu final."""
    parsed = urlparse(url)
    if not parsed.scheme:
        return True
    return any(parsed.path.lower().endswith(ext) for ext in ALLOWED_EXTS)

def get_image_urls_from_page(html: str, page_url: str):
    """Funció que extrey la soup d'una url i n'extreu la url de la imatge de la xapa"""
    soup = BeautifulSoup(html, "html.parser")
    imgs = soup.find_all("img")
    urls = []
    for img in imgs:
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        full = urljoin(page_url, src)
        if is_valid_image_url(full):
            if len(full) > 60:
                urls.append(full)
    # treu duplicates mantenint ordre
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique

def download_image(url: str, dest_folder: str, prefix, count) -> str:
    """Donada la url de la imatge de la xapa, guarda la iamtge al directori local expecificat"""
    try:
        resp = requests.get(url, headers=HEADERS, stream=True, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        return f"ERROR: {url} -> {e}"
    # extreure nom de fitxer o crear-lo
    path = urlparse(url).path
    filename = os.path.basename(path)
    if not filename:
        # fallback amb timestamp
        filename = f"image_.jpg"
    # prefix per identificar la xapa
    #safe_name = f"{prefix}_{filename}"
    safe_name = str(count).zfill(3) + ". " + str(prefix) + ".jpg"
    out_path = os.path.join(dest_folder, safe_name)
    # escriure contingut en binari
    try:
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        return f"ERROR_ESCRIPTURA: {out_path} -> {e}"
    return out_path

def process_numero(n: int, count: int):
    """Funció principal que crida a les funcions anteriors per a extreure'n imatges"""
    page_url = BASE.format(n)
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[{n}] Error obrint {page_url}: {e}")
        return
    img_urls = get_image_urls_from_page(r.text, page_url)
    if not img_urls:
        print(f"[{n}] No s'han trobat imatges a {page_url}")
        return
    print(f"[{n}] S'han trobat {len(img_urls)} imatges. Baixant...")
    for i, img_url in enumerate(img_urls, start=1):
        result = download_image(img_url, OUTPUT_DIR, n, count)
        print(f"    {img_url} -> {result}")
        time.sleep(0.1)  # petit retard entre descàrregues de la mateixa pàgina


# Començament del codi

# Primerament, esborrem les imatges del directori local, perquè, un cop acabat el codi, només hi hagi xapes dels ids especificats
carpeta = "C:/Users/usuari/Documents/Spotify/xapes/imatges_xapes"
for fitxer in os.listdir(carpeta):
    ruta_fitxer = os.path.join(carpeta, fitxer)
    if os.path.isfile(ruta_fitxer):
        os.remove(ruta_fitxer)
        print(f"Esborrat: {ruta_fitxer}")

# Anem iterant la llista amb els ids de la xapa.
# Per a cada xapa cridem a process_numero() que s'encarrega de tot lo mencionat
count = 1
for n in NUMEROS:
    process_numero(n, count)
    time.sleep(DELAY_SECONDS)
    count += 1
