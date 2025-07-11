import requests
import pandas as pd
import streamlit as st

# Filtermöglichkeiten des Katalogs vorbereiten
Thema =   ['Abfall',
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

Datentyp = ['Indikator',
            'Statistik',
            'Geodaten',
            'Geodatenmodell',
            'Monitoring',
            'Daten']

Monitoring = ['LFI',
              'NABO',
              'NABEL',
              'NADUF',
              'NAWA',
              'NAQUA',
              'LABES',
              'BDM',
              'SonBase']

# Mapping der BAFU-Themen auf das Keyword bei opendata.swiss
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

# Bafu Daten aus opendata.swiss abfragen
url = "https://opendata.swiss/api/3/action/package_search"
params = {
    "q": "organization:bundesamt-fur-umwelt-bafu",
    "rows": 1000  # Request a large number of rows to get all entries
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    if data['success']:
        packages = data['result']['results']
        df = pd.DataFrame(packages)
    else:
        print("API request was not successful.")
        print(data['error'])
else:
    print(f"Error: Failed to retrieve data. Status code: {response.status_code}")

dfOpendataSwiss = df
dfOpendataSwiss = dfOpendataSwiss[['keywords', 'title','description', 'modified']]
dfOpendataSwiss['description'] = dfOpendataSwiss['description'].apply(lambda x: x['de'] if isinstance(x, dict) and 'de' in x else None)
dfOpendataSwiss['title'] = dfOpendataSwiss['title'].apply(lambda x: x['de'] if isinstance(x, dict) and 'de' in x else None)
dfOpendataSwiss['Typ'] = 'Daten'
dfOpendataSwiss['Typ'] = dfOpendataSwiss.apply(lambda row: 'Geodatenmodell' if 'Geodatenmodell' in str(row['title']) else row['Typ'], axis=1)

# prompt: wenn ein Wort aus dem Array Monitoring in title oder description vorkommt, wird das Attribut Typ auf Monitoring gesetzt
dfOpendataSwiss['Typ'] = dfOpendataSwiss.apply(
    lambda row: 'Monitoring' if any(word in str(row['title']) or word in str(row['description']) for word in Monitoring) else row['Typ'],
    axis=1
)

# Statistiken und Indikatoren lesen
dfStatistikenIndikatoren = pd.read_excel("StatistikenIndikatoren.xlsx")

# Mapping auf Keywords
dfStatistikenIndikatoren['keywords'] = dfStatistikenIndikatoren['keywords'].apply(lambda x: [map_options(x)] if pd.notnull(x) and map_options(x) is not None else [])

# Combine the two dataframes
dfCombined = pd.concat([dfOpendataSwiss, dfStatistikenIndikatoren], ignore_index=True)

#--------------------------------------------------------------------------
# Streamlit App
#--------------------------------------------------------------------------
st.title("BAFU Datenkatalog")
