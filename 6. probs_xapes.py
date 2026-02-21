# Importem les llibreries necessàries
import pandas as pd

# Per a cada col·lecció/cava, generem la proabilitat de que tinguem la seva xapa.
# Amb això hem tingut en compte:
    # Núm. de xapes de la col·lecció i núm. de xapes d'aquella col·lecció que tinc
    # Importància de cada xapa (com més important és, més fàcil és que la pogui obtenir)
    # Data de la xapa. (Si és una xapa molt antiga, és probable que ja no s'en facin. I el contrari)
# Comentar que, manualment, al excel_xapes vaig fer inventari de les que sí tenia amb un "Sí" al camp "Colecció")

# Carreguem l'excel de xapes
xapes = pd.read_excel('C:/Users/usuari/Documents/Spotify/xapes/XAPES bbdd/Excel_xapes.xlsx')

# Agafem només aquelles col·leccions que ja tenim alguna xapa (perque sinó, aquella cava sería 0%)
caves_distinctes = xapes.loc[xapes['Colecció'] == 'Sí', 'Cava'].unique()

# Les posem totes en una llista
caves_distinctes = (
    xapes.loc[xapes['Colecció'] == 'Sí', 'Cava']
      .drop_duplicates()
      .tolist()
)

# Convertim totes les col·leccions en strings i les ordenem alfabèticament
alf_caves_distinctes = sorted(map(str, caves_distinctes))

# Iterem cada col·lecció
for cava in alf_caves_distinctes:
    # Hem de tornar a convertir les col·leccions (que siguin possibles) en números
    try:
        cava = int(cava)
    except:
        pass
    # Seleccionem les xapes d'aquella col·lecció
    xapes_coleccio0 = xapes[xapes['Cava'] == cava]

    # Si la col·lecció només te una xapa, és que tenim 1/1, per tant, és un 100% de probabilitat que ja la tinguem
    if len(xapes_coleccio0) == 1:
        print(cava, ": 100% -", 1, 1)
    # Si no
    else:
        # Fem 5 quantils (segons l'id) de les 15 xapes més importants d'aquella col·lecció
        # L'id marca com de nova o vella és una xapa
        percentils_top15 = xapes_coleccio0[:15]['id'].quantile([0.1, 0.25, 0.5, 0.75, 0.9])

        bins = [0, percentils_top15[0.1], percentils_top15[0.25], percentils_top15[0.5], percentils_top15[0.75],
                percentils_top15[0.9], float('inf')]
        # Aquests seràn els pesos als quals se'ls hi multiplicarà a cada xapa segons a quin percentil queda el seu id
        labels = [0.9, 0.95, 0.98, 1.02, 1.05, 1.1]

        # Fem una còpia de les xapes d'aquella col·lecció
        xapes_coleccio = xapes_coleccio0.copy()

        # Hi afegim el multiplicador corresponent (label) a cada xapa segons els bins (quantils)
        xapes_coleccio['multiplicador'] = pd.cut(
            xapes_coleccio['id'],
            bins=bins,
            labels=labels,
            include_lowest=True
        ).astype(float)

        # Hi apliquem el multiplicador a la Puntuació, generant la columna "Puntuació_altered"
        xapes_coleccio.loc[:, 'Puntuació_altered'] = (
                xapes_coleccio['Puntuació'] * xapes_coleccio['multiplicador'])

        # Perque hi hagi més diferència entre les xapes amb + i - importpancia, elevem cada puntuació a 6
        # Calculem la puntuació total d'una col·lecció
        puntuacio_total = {valor_xapa**6 for valor_xapa in xapes_coleccio['Puntuació_altered']}
        # Calculem la puntuació parcial (només les xapes que Sí tenim) d'una col·lecció
        puntuacio_parcial = {valor_xapa**6 for valor_xapa in xapes_coleccio[xapes_coleccio['Colecció'] == 'Sí']['Puntuació_altered']}

        # Per a cada cava/col·lecció dividim la punt_parcial entre la punt_total per treure el percentatge
        print(cava, ":", round((sum(puntuacio_parcial)*100)/sum(puntuacio_total),8), "% -", len(puntuacio_parcial), len(puntuacio_total))
