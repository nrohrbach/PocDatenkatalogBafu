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
st.title("BAFU Datenkatalog")

# Suchfeld
search_query = st.text_input("Suche nach Titel oder Beschreibung")

# Filter Dropdowns
selected_thema = st.selectbox("Filter nach Thema", ["Alle"] + Thema)
selected_typ = st.selectbox("Filter nach Typ", ["Alle"] + Datentyp)

# --- Filterlogik ---
filtered_df = dfCombined.copy()

# Suche nach Text
if search_query:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: (
                search_query.lower() in str(row['title']).lower() or
                search_query.lower() in str(row['description']).lower()
            ),
            axis=1
        )
    ]

# Filter nach Thema
if selected_thema != "Alle":
    # Wenden Sie die map_options Funktion hier an, um das opendata.swiss Keyword zu erhalten
    mapped_thema = map_options(selected_thema)
    if mapped_thema:
        # Filtern Sie, wenn das gemappte Keyword in der 'keywords' Liste vorhanden ist
        filtered_df = filtered_df[
            filtered_df['keywords'].apply(
                lambda keywords_list: mapped_thema in keywords_list if isinstance(keywords_list, list) else False
            )
        ]


# Filter nach Typ
if selected_typ != "Alle":
    filtered_df = filtered_df[filtered_df['Typ'] == selected_typ]

# --- Anzeige der Ergebnisse ---

st.subheader(f"Resultate ({len(filtered_df)} gefunden)")

if filtered_df.empty:
    st.info("Keine Ergebnisse gefunden.")
else:
    # Farben für die Buttons (Beispielhafte Farben, können angepasst werden)
    thema_colors = {thema: f"#{abs(hash(thema)) % (2**24):06x}" for thema in Thema}
    typ_colors = {typ: f"#{abs(hash(typ) * 2) % (2**24):06x}" for typ in Datentyp}

    for index, row in filtered_df.iterrows():
        # Erstelle einen eindeutigen Schlüssel für das Expander-Widget
        expander_key = f"expander_{row['title']}_{index}"

        with st.expander(row['title'], expanded=False):
            # Thema Button
            thema_value = row['keywords']
            # Finden Sie den BAFU-Themennamen basierend auf dem opendata.swiss Keyword
            bafu_thema_name = None
            if isinstance(thema_value, list) and thema_value:
                 # Versuchen Sie, das erste Keyword in ein BAFU Thema zurückzusetzen
                 for key, val in map_options.mapping.items(): # Greifen Sie auf die interne Mapping-Variable zu
                     if val == thema_value[0]:
                         bafu_thema_name = key
                         break

            if bafu_thema_name:
                 st.markdown(
                     f'<button style="background-color: {thema_colors.get(bafu_thema_name, "#cccccc")}; color: white; border: none; padding: 5px 10px; margin: 2px; border-radius: 4px;">{bafu_thema_name}</button>',
                     unsafe_allow_html=True
                 )

            # Typ Button
            typ_value = row['Typ']
            st.markdown(
                f'<button style="background-color: {typ_colors.get(typ_value, "#cccccc")}; color: white; border: none; padding: 5px 10px; margin: 2px; border-radius: 4px;">{typ_value}</button>',
                unsafe_allow_html=True
            )

            st.write(f"**Beschreibung:** {row['description']}")
            st.write(f"**Zuletzt geändert:** {row['modified']}")
            # Hier können Sie weitere Details anzeigen, z.B. Links zu den Daten


# --- Ausführen der App ---
# Speichern Sie diesen Code als eine .py Datei, z.B. app.py
# In Google Colab können Sie Streamlit Apps wie folgt ausführen:
# !streamlit run app.py & npx localtunnel --port 8501
# Führen Sie diesen Befehl in einer Zelle aus, nachdem Sie den Code als Datei gespeichert haben.
# Der Link zum Öffnen der App wird im Output von localtunnel angezeigt.

