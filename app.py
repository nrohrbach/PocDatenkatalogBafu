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
            'Daten',
            'Daten von Webseite']

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
#--------------------------------------------------------------------------
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

# Funktion welche Keywords extrahiert
def extract_keywords(x):
           if isinstance(x, dict):
                      return set().union(*x.values())
           elif isinstance(x, list):
                      return set(x)
           elif isinstance(x, str):
                      return {x}
           else:
                      return set()


# Funktion welche Daten aus opendata.swiss und Indikatoren abfragt
#--------------------------------------------------------------------------
@st.cache_data
def get_bafu_data():
  """
  Fetches data packages from the opendata.swiss API for the BAFU organization.

  Returns:
      pandas.DataFrame or None: A DataFrame containing the data packages if the
                                 API request is successful, otherwise None.
  """
  url = "https://opendata.swiss/api/3/action/package_search"
  params = {
      "q": "organization:bundesamt-fur-umwelt-bafu",
      "rows": 1000  # Request a large number of rows to get all entries
  }
  try:
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()

    if data['success']:
        packages = data['result']['results']
        df = pd.DataFrame(packages)
        dfOpendataSwiss = df
        dfOpendataSwiss['URL'] = 'https://opendata.swiss/de/dataset/' + dfOpendataSwiss['title_for_slug']
        dfOpendataSwiss['Kontakt'] = dfOpendataSwiss['maintainer_email']
        dfOpendataSwiss = dfOpendataSwiss[['keywords', 'title','description', 'modified','issued','Kontakt','URL',]]
        dfOpendataSwiss['description'] = dfOpendataSwiss['description'].apply(lambda x: x['de'] if isinstance(x, dict) and 'de' in x else None)
        dfOpendataSwiss['title'] = dfOpendataSwiss['title'].apply(lambda x: x['de'] if isinstance(x, dict) and 'de' in x else None)
        dfOpendataSwiss['Typ'] = 'Daten'
        dfOpendataSwiss['Typ'] = dfOpendataSwiss.apply(lambda row: 'Geodatenmodell' if 'Geodatenmodell' in str(row['title']) else row['Typ'], axis=1)
        
        # prompt: wenn ein Wort aus dem Array Monitoring in title oder description vorkommt, wird das Attribut Typ auf Monitoring gesetzt
        dfOpendataSwiss['Typ'] = dfOpendataSwiss.apply(lambda row: 'Monitoring' if any(word in str(row['title']) or word in str(row['description']) for word in Monitoring) else row['Typ'], axis=1)

        # Statistiken und Indikatoren lesen
        urlexcel = 'https://uvek-gis.admin.ch/BAFU/umweltdaten/opendata.swiss/StatistikenIndikatoren.xlsx'
        dfStatistikenIndikatoren = pd.read_excel(urlexcel, engine="openpyxl")

        # Mapping auf Keywords
        dfStatistikenIndikatoren['keywords'] = dfStatistikenIndikatoren['keywords'].apply(lambda x: [map_options(x)] if pd.notnull(x) and map_options(x) is not None else [])
        
        # Combine the two dataframes
        dfCombined = pd.concat([dfOpendataSwiss, dfStatistikenIndikatoren], ignore_index=True)

        return dfCombined
    else:
        print("API request was not successful.")
        print(data.get('error', 'No error message provided.'))
        return None
  except requests.exceptions.RequestException as e:
      print(f"Error fetching data: {e}")
      return None

             
dfCombined = get_bafu_data()

#--------------------------------------------------------------------------
# Streamlit App
#--------------------------------------------------------------------------
# Streamlit App
st.title("BAFU Datenkatalog")

# Fetch data
dfCombined = get_bafu_data()

if dfCombined is not None:
    # Search bar
    search_query = st.text_input("Suche nach Titel oder Beschreibung")

    # Filter by Thema using checkboxes
    st.sidebar.subheader("Themenfilter")
    selected_themen = []
    for thema_option in Thema:
        if st.sidebar.checkbox(thema_option):
            selected_themen.append(thema_option)

    # Filter by Typ using selectbox (remains for now)
    selected_typ = st.selectbox("Filter nach Typ:", ["Alle"] + Datentyp)


    # Apply filters
    filtered_df = dfCombined.copy()

    if search_query:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['description'].str.contains(search_query, case=False, na=False)
        ]

    # Apply Thema filter from checkboxes
    if selected_themen:
        mapped_selected_themen = [map_options(t) for t in selected_themen if map_options(t) is not None]

        if mapped_selected_themen:
           filtered_df = filtered_df[
                   filtered_df['keywords'].apply(
                              lambda x: bool(extract_keywords(x) & set(mapped_selected_themen))
                   )
                   ]
           
            #filtered_df = filtered_df[
             #   filtered_df['keywords'].apply(lambda x: any(keyword in mapped_selected_themen for keyword in x) if isinstance(x, list) else False)
            #]


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
                if 'Kontakt' in row and pd.notnull(row['Kontakt']):
                     st.write(f"**Kontakt:** [{row['Kontakt']}]({row['Kontakt']})")
                if 'URL' in row and pd.notnull(row['URL']):
                     st.write(f"**Download:** [{'Daten herunterladen'}]({row['URL']})")

    else:
        st.info("Keine Einträge gefunden, die den Kriterien entsprechen.")
else:
    st.error("Fehler beim Laden der Daten.")

