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
urlexcel = 'https://uvek-gis.admin.ch/BAFU/umweltdaten/opendata.swiss/StatistikenIndikatoren.xlsx'
dfStatistikenIndikatoren = pd.read_excel(urlexcel, engine="openpyxl")

# Mapping auf Keywords
dfStatistikenIndikatoren['keywords'] = dfStatistikenIndikatoren['keywords'].apply(lambda x: [map_options(x)] if pd.notnull(x) and map_options(x) is not None else [])

# Combine the two dataframes
dfCombined = pd.concat([dfOpendataSwiss, dfStatistikenIndikatoren], ignore_index=True)

#--------------------------------------------------------------------------
# Streamlit App
#--------------------------------------------------------------------------
# Streamlit App
st.title("BAFU Datenkatalog")

# Search bar
search_query = st.text_input("Suche nach Titel oder Beschreibung")

# Filters
selected_thema = st.selectbox("Filter nach Keyword:", ["Alle"] + Thema)
selected_typ = st.selectbox("Filter nach Typ:", ["Alle"] + Datentyp)

# Apply filters
filtered_df = dfCombined.copy()

if search_query:
    filtered_df = filtered_df[
        filtered_df['title'].str.contains(search_query, case=False, na=False) |
        filtered_df['description'].str.contains(search_query, case=False, na=False)
    ]

if selected_thema != "Alle":
    filtered_df = filtered_df[
        filtered_df['keywords'].apply(lambda x: any(map_options(selected_thema) in kw for kw in x) if isinstance(x, list) else False)
    ]


if selected_typ != "Alle":
    filtered_df = filtered_df[filtered_df['Typ'] == selected_typ]

# Display results
st.subheader(f"Gefundene Einträge: {len(filtered_df)}")

if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        with st.expander(f"**{row['title']}**"):
            st.write(f"**Typ:** {row['Typ']}")
            st.write(f"**Beschreibung:** {row['description']}")
            if 'modified' in row and pd.notnull(row['modified']):
                st.write(f"**Zuletzt geändert:** {row['modified']}")
            if 'url' in row and pd.notnull(row['url']):
                 st.write(f"**Link:** [{row['url']}]({row['url']})")

else:
    st.info("Keine Einträge gefunden, die den Kriterien entsprechen.")
