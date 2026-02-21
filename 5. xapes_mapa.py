# Importem les llibreries necessàries
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from datetime import datetime


# Generem un mapa HTML on es pot observar els llocs amb més caves i marques

# Llegim el csv generat al script anterior (4), i amb les modificaciosn manuals realitzades a posterior:
ranking1 = pd.read_csv('C:/Users/usuari/Documents/Spotify/xapes/XAPES bbdd/ranking1.csv')
ranking1['Municipi'] = ranking1['Municipi'].str.upper()

# Obtenim la data actual
today = datetime.today()
formatted_date = today.strftime('%Y%m%d')

# Inicializem el geolocalizador
geolocator = Nominatim(user_agent="mapa_municipis")

# Creem una llista per guardar-hi les dades del municipi
dades_municipi = []

# Agrupem tots els registres per municipis
grouped = ranking1.groupby('Municipi')
# Creem una llista amb el dataset/grup de cada municipi
grouped_list = [(name, group) for name, group in grouped]


# Per cada municipi del dataset
for municipi, group in grouped_list:
    # N'agafem la comarca
    comarca = group['Comarca'].iloc[0]
    provinica = group['Província'].iloc[0]
    # Si el municpi no és "-"
    if municipi != '-':
        compt = 0
        while compt < 10:
            try:
                # Cas normal
                if isinstance(comarca, str):
                    # Trobem la location indicant municipi i comarca
                    location = geolocator.geocode([municipi, comarca])
                # Cas especial 1: No tenim comarca
                elif isinstance(comarca, float):
                    # Trobem la location indicant el municipi i provincia
                    location = geolocator.geocode([municipi, provinica])
                # Cas especial d'Aiguafreda (la llibereria el considera d'Osona)
                if municipi == 'Aiguafreda':
                    # Trobem la location indicant el municipi i la comarca Osona
                    location = geolocator.geocode([municipi, 'Osona'])
                # Casos especials (entrant la comarca, la llibreria el classifica malament)
                if municipi in ["l'Ametlla de Mar", "Sant Pol de Mar"]:
                    location = geolocator.geocode(municipi)
                print(municipi, "-", location, location.latitude, location.longitude)
                compt = 10
            except:  # Evitar error: geopy.exc.GeocoderUnavailable: HTTPSConnectionPool(host='nominatim.openstreetmap.org', port=443): Max retries exceeded
                compt += 1

        # Si no hi ha hagut cap problema per trobar la location
        if location:
            try:
                # Extreiem les columnes Cava & Puntuació del dataset
                caves_info = ranking1[ranking1['Municipi'] == municipi][['Cava', 'Puntuació']]
                # Ho passem a HTML
                caves_info_html = caves_info.to_html(index=False,escape=False)
                print(sum(caves_info['Puntuació']))
                # Afegim totes les dades del muncipi que voldrem mostrar
                dades_municipi.append({
                    "Municipi": municipi,
                    "lat": location.latitude,
                    "lon": location.longitude,
                    "Habitants": round(group['Població'].iloc[0]),
                    "Nre. puntuacions": ranking1[ranking1['Municipi'] == municipi].shape[0],
                    "Puntuació total": int(sum(caves_info['Puntuació'])),
                    "Caves": caves_info_html
                })
            except:
                print(f"Error pel: {municipi}")
        else:
            print(f"No s'ha pogut geodificar el municipi: {municipi}")


# Convertim las dades_municipi a un DataFrame
coord_df = pd.DataFrame(dades_municipi)


# Creem el Mapa
mapa = folium.Map(location=[coord_df['lat'].mean(), coord_df['lon'].mean()], zoom_start=6)

# Funció que, segons la Puntuació, seleccionarà un color més fosc o més clar
def color(puntuacio):
    if puntuacio < 500:
        return 'lightgreen'
    elif puntuacio < 1000:
        return 'green'
    elif puntuacio < 5000:
        return 'darkgreen'
    elif puntuacio < 10000:
        return 'cadetblue'
    elif puntuacio < 50000:
        return 'darkblue'
    else:
        return 'black'


titol = f'''
     <div style="position: fixed; 
                 top: 10px; left: 50%; transform: translateX(-50%);
                 z-index:9999; font-size:20px; background-color:lightgreen; padding: 10px;
                 border:2px solid darkgreen;
                 text-align: center;">
     <b>Mapa de Caves<br></b>
     <span style="font-size: 12px;">Arnau Garriga Riba - {today.strftime("%d/%m/%Y")}</span>
     </div>
     '''
mapa.get_root().html.add_child(folium.Element(titol))


llegenda_color = '''
     <div style="position: fixed; 
                 bottom: 20px; right: 20px; width: 210px; height: 170px; 
                 border:2px solid grey; z-index:9999; font-size:15px;
                 background-color:white;
                 padding: 10px;
                 ">
    <b>Significat dels colors:</b><br>
     <i style="color:lightgreen; -webkit-text-stroke: 0.3px black;">< 500 Puntuació Total<br></i>
     <i style="color:green; -webkit-text-stroke: 0.3px black;">< 1000 Puntuació Total<br></i>
     <i style="color:darkgreen; -webkit-text-stroke: 0.3px black;">< 5000 Puntuació Total<br></i>
    <i style="color:cadetblue; -webkit-text-stroke: 0.3px black;">< 10000 Puntuació Total<br></i>
     <i style="color:darkblue; -webkit-text-stroke: 0.3px black;">< 50000 Puntuació Total<br></i>
     <i style="color:black; -webkit-text-stroke: 0.3px black;">>= 50000 Puntuació Total</i>
     </div>
     '''

mapa.get_root().html.add_child(folium.Element(llegenda_color))


# Definim l'estructura de cada icona al mapa
for _, row in coord_df.iterrows():
    popup_content = f"""
    <b>Municipi:</b> {row['Municipi']}<br>
    <b>Habitants:</b> {row['Habitants']}<br>
    <b>Nre. puntuacions:</b> {row['Nre. puntuacions']}<br>
    <b>Suma de puntuacions:</b> {row['Puntuació total']}<br>
    <b>Puntuació total entre habitants:</b> {str(round(row['Puntuació total'] / row['Habitants'],3)).replace('.', ',')}<br>
    <b>Caves:</b><br>
    <div style="max-height: 200px; overflow-y: auto;">
        {row['Caves']}
    </div>
    """
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(popup_content, max_width=300),
        icon=folium.Icon(color=color(row['Puntuació total']), icon='info-sign')
    ).add_to(mapa)


# Guardem el mapa com un document HTML
mapa.save('mapa_caves_'+str(formatted_date)+".html")