import streamlit as st
import numpy as np
import pandas as pd
import requests

# Definiere die Liste der Optionen
options = ['Abfall',
           'Altlasten',
           'Bildung, Forschung, Innovation',
           'Biodiversität',
           'Biotechnologie',
           'Boden',
           'Chemikalien',
           'Elektrosmog und Licht',
           'Ernährung, Wohnen, Mobilität',
           'Gesundheit',
           'Internationales',
           'Klima',
           'Landschaft',
           'Lärm',
           'Luft',
           'Naturgefahren',
           'Recht',
           'Störfallvorsorge',
           'Umweltverträglichkeitsprüfung',
           'Wald & Holz',
           'Wasser',
           'Wirtschaft und Konsum'
           ]

def map_options(option):
  mapping = {
      'Abfall': 'abfall',
      'Altlasten': 'altlasten',
      'Bildung, Forschung, Innovation': 'bildung',
      'Biodiversität': 'biodiversitat',
      'Biotechnologie' : 'biotechnologie',
      'Boden' : 'boden',
      'Chemikalien' : 'chemikalien',
      'Elektrosmog und Licht' : 'elektrosmog',
      'Ernährung, Wohnen, Mobilität'  : 'ernaehrung',
      'Gesundheit'  : 'gesundheit',
      'Internationales'  : 'internationales',
      'Klima'  : 'klima',
      'Landschaft'  : 'landschaft',
      'Lärm'  : 'laerm',
      'Luft'  : 'luft',
      'Naturgefahren'  : 'naturgefahren',
      'Recht'  : 'recht',
      'Störfallvorsorge'  : 'storfallvorsorge',
      'Umweltverträglichkeitsprüfung'  : 'umweltvertraeglichkeitpruefung',
      'Wald & Holz'  : 'wald',
      'Wasser'  : 'wasser',
      'Wirtschaft und Konsum'  : 'wirtschaft'
  }
  return mapping.get(option, None) # Return None if option is not found

# Funktion fragt alle Datensätze von opendata.swiss nach einem Keyword ab
def search_datasets(keyword):
    # Basis-URL der CKAN API
    base_url = "https://opendata.swiss/api/3/action/package_search"
    
    # Parameter für die Abfrage
    params = {
        "fq": f"organization:{'bundesamt-fur-umwelt-bafu'}",
        "q": f"keywords_de:{keyword}"
    }
    
    # Anfrage an die API senden
    response = requests.get(base_url, params=params)
    data = response.json()
    data = data["result"]["results"]

    # Daten aus Json auslesen
    description = [s['description']['de'] for s in data]
    title = [s['title']['de'] for s in data]
    url0 = [s['resources'][0]['url'] for s in data]
    title0 = [s['resources'][0]['title']['de'] for s in data]
    url1 = [s['resources'][1]['url'] for s in data]
    title1 = [s['resources'][1]['title']['de'] for s in data]

    # Daten als Dataframe speichern
    dict = {'title': title, 'description': description, 'url0': url0, 'title0': title0, 'url1': url1, 'title1': title1}
    dfOpendataSwiss = pd.DataFrame(dict)

    return dfOpendataSwiss


st.title("PoC BAFU Datenkatalog")

st.markdown(
    """
Beschreibung

"""
)

st.header("Thema auswählen")
# Erstelle das Auswahlfenster
selected_option = st.selectbox("Wähle ein Thema aus:", options)

# Verwende die map_options Funktion mit der ausgewählten Option
mapped_option = map_options(selected_option)

# Verwende die Abfrage opendata.swiss mit dem gemappten Thema
dfOGD = search_datasets(mapped_option)

#Antwort
st.subheader("OGD Publikationen des BAFU zum Thema")
st.dataframe(dfOGD)

# Zeige die gemappte Option an
if mapped_option:
    st.write(f"Du hast {selected_option} ausgewählt, das gemappte Thema ist: {mapped_option}.")
