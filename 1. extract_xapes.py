# Importem les llibreries necessàries
import re
import time
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
import pandas as pd

# Script que va iterant les diferents xapes de xapes.net i les afegeix en un csv.
    # Per a cada registre (xapa) hi ha:
        # id
        # Cava: marca
        # Col·lecció: Quanta gent la té a la col·lecció
        # Repetides: Quanta gent la té repetida
        # Puntuació: Score/puntuació a la xapa segons els valors de Col·lecció i Repetides

# headers necessaris pels request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36"
}

def extract_following_value(strong_tag):
    """
    Recorre els next_siblings del <strong> i retorna el primer
    text o nombre útil que trobi.
    """
    for sib in strong_tag.next_siblings:
        # String directe (navegable)
        if isinstance(sib, NavigableString):
            text = sib.strip()
            if text:
                m = re.search(r'\d[\d.,]*', text)   # primer nombre del text
                return m.group(0) if m else text
        # Si és un Tag (ex: <span>, <a>, <br/>, ...)
        elif isinstance(sib, Tag):
            text = sib.get_text(strip=True)
            if text:
                m = re.search(r'\d[\d.,]*', text)
                return m.group(0) if m else text
    return ''  # si no troba res

# creem un diccionari xapes_dict buit. Aquest serà l'objecte on hi anirem guardant les xapes
xapes_dict = {}

# Anem iterant les diferents xapes de "xapes.net" i les afegim a la llista
# Com que hi ha moltes xapes, i per tant, tardaria molt, ho hem anat fent per trossos (especificant els indexs de la primera xapa a iterar fins a l'última)
    # En aquest cas, va de la xapa amb id=240000 (registrada el 23/03/2024 16:42) fins a la del id=256000 (registrada el 06/10/2025 07:54)
iter1 = 240000
iter2 = 256000
for x in range(iter1, iter2):
    # Preparem la url
    url = f"https://www.xapes.net/ca/xapa/{x}/caves"
    # Afegim al xapa al xapes_dict com a un diccionari buit
    xapes_dict[x] = {}
    try:
        # Fem un request a la url i n'extreiem la soup (contingut) utilitzant BeautfulSoup
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"[{x}] HTTP {resp.status_code}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        print(f"--- Xapa id {x} ---")

        # Seleccionem els "strongs" de la url
        strongs = soup.find_all("strong")
        if not strongs:
            print("No s'han trobat <strong> a la pàgina")
            continue

        # Iterem els "strongs" del contingut
        for st in strongs:
            # De cada "strong", n'extreiem la parelleta de label i el seu value
            label = st.get_text(strip=True).rstrip(':')
            value = extract_following_value(st)
            if value:
                if label == 'Col·lecció':
                    # Aquests "if" i "else" fan que si és una xapa que molta gent té a la col·lecció, faci un print amb varis "-" perque es vegi més fàcilment a la consola
                    # (És per unes proves que havia fet al començament)
                    if int(value) >= 1100:
                        print(label, ":", value, "-----------------------------------------------------")
                    else:
                        print(f"{label}: {value}")
                    # Afegim per a la xapa, quanta gent la té a la col·lecció
                    value_c = value
                    xapes_dict[x]['Col·lecció'] = value_c
                elif label == 'Repetides':
                    # Afegim per a la xapa, quanta gent la té repetida
                    value_r = value
                    xapes_dict[x]['Repetides'] = value_r
                # Afegim per a la xapa, de quin cava (marca) més
                elif label in ['Caves', 'Estrangeres', 'Marquistes', 'Pirules', 'Especulació', 'Autonòmiques', 'Pendents identificar / Varis']:
                    xapes_dict[x]['Cava'] = value
            else:
                print(f"{label}: (no trobat)")
        # Afegim per a la xapa, la "Puntació", que dóna una importància a la xapa segons els valors de Col·lecció i Repetides
        xapes_dict[x]['Puntuació'] = 2 * int(value_r) + int(value_c)

        # Petita pausa per ser polit amb el servidor
        time.sleep(0.15)

        # Quan arribem a un id que acaba amb "999" guardem totes les xapes iterades a un csv
        if str(x)[-3:] == '999':
            # Convertir a DataFrame
            df = pd.DataFrame.from_dict(xapes_dict, orient='index')

            # Afegir la columna 'id' (els índexs originals)
            df.reset_index(inplace=True)
            df.rename(columns={'index': 'id'}, inplace=True)

            # Reordenar les columnes si cal
            df = df[['id', 'Cava', 'Col·lecció', 'Repetides', 'Puntuació']]

            # Exportar a CSV
            df.to_csv('caves15.csv', index=False, encoding='utf-8')

            # Després, manualment i fora del script, hem ajuntat tots aquests csvs generats en un únic excel

    except Exception as e:
        print(f"[{x}] Error: {e}")