# Importem les llibreries necessàries
import pandas as pd


# Afegim la "Comarca", "Província" i "Població" (num_habitants) de cada registre creuant amb un df amb info de municipis


# Llegim el csv generat al script anterior (3), pero:
    # amb modificacions manuals prèvies:
        # en les quals hem limitat el número de caves (files) a 1000
        # en les quals s'ha afegit el municipi en els registres que no l'agafava desde la soup
ranking0 = pd.read_csv('C:/Users/usuari/Documents/Spotify/xapes/XAPES bbdd/ranking0_modified.csv')

# Inicialitzem les columnes de comarca, província i població (num_habitants)
ranking0['Comarca'] = ''
ranking0['Província'] = ''
ranking0['Població'] = ''

# Carreguem un csv "poblacions_2" amb informació de tots els municipis de CAT, VAL I BAL
poblacions2 = pd.read_csv('C:/Users/usuari/Documents/Spotify/xapes/XAPES bbdd/poblacions_2.csv')
poblacions2['Municipi'] = poblacions2['Municipi'].str.upper()

# Iterem totes les files del df ranking0, creuant amb el poblacions2 per obtenir-ne la Comarca, Provincia i Població
for index, row in ranking0.iterrows():
    try:
        row_muni = poblacions2[poblacions2['Municipi'] == row['Municipi'].upper()]
        ranking0.loc[index, 'Comarca'] = row_muni['Comarca'].iloc[0]
        ranking0.loc[index, 'Província'] = row_muni['Província'].iloc[0]
        ranking0.loc[index, 'Població'] = row_muni['Població'].iloc[0]
    except:
        pass

print(ranking0.head(20))

# Guardem el df a local com a ranking1.csv
ranking0.to_csv("C:/Users/usuari/Documents/Spotify/xapes/XAPES bbdd/ranking1.csv", index=False)

# Hi ha caves/marques que són de fora dels països catalans (ex: frança, La Rioja...)
    # Aquests no es trobaven al poblacions_2 per lo qual no han creuat.
    # A aquests casos els hi hem afegit la Província i Població manualment