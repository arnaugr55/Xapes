# Importem les llibreries necessàries
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

## Donat l'excel de xapes, agrupem per marca/cava i fem un ranking de caves
# La puntuació de cada cava té en compte el número de xapes que té i la puntuació de les seves xapes
# També localitzem el cava en el seu municipi

# Carreguem l'excel de xapes. Com que és un excel molt gran, per a les proves s'ha utilitzat un de reduït
xapes = pd.read_excel('C:/Users/usuari/Documents/Spotify/xapes/XAPES bbdd/Excel_xapes.xlsx')
#xapes = pd.read_excel('C:/Users/usuari/Documents/Spotify/xapes/XAPES bbdd/Excel_xapes_mini.xlsx')

# De l'excel, seleccionem només la columna de puntuació
cols_puntuacio = [col for col in xapes.columns if "Puntuació" in col]

# Per calcular la puntuació d'una columna:
    # 1- Agrupem per marca, cava
    # 2- A cada xapa, elevem la seva puntuació a 5
    # 3- Fem la suma d'aquests resultats per a cada cava
    # 4- Aquesta suma l'elevam a 0.16 per reduir-la
# Amb això, queden totes les caves amb una escala del 0 al 100.
resultat = (
    xapes
    .assign(**{col: xapes[col]**5 for col in cols_puntuacio})      # eleva puntuacions
    .groupby('Cava')
    .agg({
        **{col: "sum" for col in cols_puntuacio},   # suma puntuacions
        "id": "first"                               # guarda un id d'exemple
    })
    .reset_index()
    .sort_values('Puntuació', ascending=False)
)
resultat.rename(columns={"id": "id_xapa"})
resultat["Puntuació"] = (resultat["Puntuació"] ** 0.16).round(2)

# Havent fet això, tenim un df on cada registre és un cava diferent
# Per a cada registre tenim:
    # "Cava": Nom del cava
    # "Puntuació": Puntuació d'aquell cava
    # "id": Id de la xapa amb més "Puntució" d'aquell cava



# Inicialitzem la columna del municipi
resultat['Municipi'] = ''
# Inicialitzem la columna del id del cava
resultat['id_cava'] = ''

# headers necessaris pels requests
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36"
}

# Ara iterem cada cava per afegir-li l'id i el municipi
for index, row in resultat.iterrows():
    error = False
    municipi = ''

    # Primer entrarem a la url de la xapa
    url = f"https://www.xapes.net/ca/xapa/{row['id']}/caves"

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"[{index}] HTTP {resp.status_code}")
            continue
        soup = BeautifulSoup(resp.text, "html.parser")

        # De la soup de la xapa, n'extreiem tots els links
        links = [a['href'] for a in soup.find_all('a', href=True)]

        # Filtrem només els que contenen "infocava"
        link_infocava = [link for link in links if "infocava" in link][0]
    except:
        error = True
        pass
    if not error:
        # En aquest link_infocava ja hi trobem el id_cava, que el guardem com a numero_cava i l'insertem al df
        numero_cava = re.search(r"/(\d+)/", link_infocava).group(1)
        resultat.loc[index, 'id_cava'] = numero_cava

        # Obtenim la soup del link_infocava, on hi haurà el municipi
        try:
            resp = requests.get(link_infocava, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"[{x}] HTTP {resp.status_code}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
        except:
            pass

        try:
            # Dins de la soup del link_infocava, el municipi no es troba molt ben especificat
                # per lo qual hem de fer varis tractaments per obetnir-lo i deixar-lo lo més net possible
                # De normal aquest ve dins del quadre de text "Adreça", en una línia que comença amb el Codi Postal
                    # Exemple: 08735 Vilobí del Penedès - (Barcelona)
            cava = soup.find("meta", attrs={"property": "og:description"})["content"]

            # Agafem el contingut dins del quadre de text "Adreça"
            adreca_h4 = soup.find("h4", string=re.compile(r"Adreça"))
            if adreca_h4:
                # Agafem tot el contingut següent dins del div/well
                parent = adreca_h4.find_next_sibling()  # o parent div segons estructura
                if not parent:
                    parent = adreca_h4.parent

                # Obtenim tot el text dins el bloc
                text = parent.get_text(separator="\n")
                # Busquem línies que comencin amb 5 dígits (codi postal, ja que en elles hi ha el nom del muncipi)
                resultats = [line.strip() for line in text.splitlines() if re.match(r"^\d{5}\b", line)]
                # Agafem la primera, ja que en alguns casos hi ha vàries línies amb CodPostal o núm teleèfon al inici
                text = resultats[0]
                # Treiem codi postal inicial
                text_sense_cp = re.sub(r"^\d{5}\s*-?\s*", "", text)
                # Treiem la província entre parèntesis
                text_sense_prov = re.sub(r"\s*\(.*?\)", "", text_sense_cp)
                # Treiem punt final si hi ha (alguns pocs casos)
                text_sense_prov = text_sense_prov.rstrip(".")
                # Agafem l'última paraula després de l'últim guió, si hi ha guions (casos especials)
                parts = text_sense_prov.split(" - ")
                # Seleccionem l'últim segment, que no està entre parèntesis
                municipi = parts[-1].strip()
                # Cas especial que el municipi acaba amb "- ". S'elimina aquesta part.
                if municipi[-1] == '-':
                    municipi = municipi[:-2]

                # Ja s'ha tractat tot, imprimim per pantalla el municipi i el guardem al df
                print("Cava:", index, cava, municipi)
                resultat.loc[index, 'Municipi'] = municipi.rstrip()
        except:
            resultat.loc[index, 'Municipi'] = '-'
    else:
        resultat.loc[index, 'Municipi'] = '-'

# Alguns municipis estàn escrits malament a la web, o hi ha un poble en comptes del municipi
    # Aquests es tradueixen automàticament amb el nom del municipi correcte

# Hi ha casos que els traduim amb un replace fent (1 --> 1)
resultat['Municipi'] = resultat['Municipi'].replace({
    "Sant Sadurni d'Anoia": "Sant Sadurní d'Anoia",
    "Sant Sadurní d’Anoia": "Sant Sadurní d'Anoia",
    'El Plà del Penedès': 'El Pla del Penedès',
    'Guardiola de Font-Rubí': 'Font-rubí',
    'La Granada del Penedès': 'La Granada',
    'Lavern-Subirats': 'Subirats',
    'Els Monjos': 'Santa Margarida i els Monjos',
    'Sant Marçal': 'Castellet i la Gornal',
    'Sant Pere Molanta': 'Olèrdola',
    'San Pere de Riudebitlles': 'Sant Pere de Riudebitlles'
})
# Hi ha casos que els traduim amb un .loc al df fent (n --> 1)
resultat.loc[resultat['Municipi'].str.contains('rdal', case=False, na=False), 'Municipi'] = 'Subirats'
resultat.loc[resultat['Municipi'].str.contains('soliveres', case=False, na=False), 'Municipi'] = 'Piera'

# Guardem el csv a local
resultat.to_csv("C:/Users/usuari/Documents/Spotify/xapes/XAPES bbdd/ranking0.csv", index=False)

# Cal comentar, que, a pesar d'haver fet moltes correccions automàtiques de municipis, n'hi ha que no s'han
    # agafat correctament (o bàsicament no ha agafat cap municipi). Aquests casos els hem tractat ja en local,
    # editant el csv manualment.