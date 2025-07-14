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
#--------------------
def prepare_bafu_data():
  """
  Fetches BAFU data from opendata.swiss, reads an Excel file for statistics,
  and combines and processes the dataframes.

  Returns:
      pandas.DataFrame or None: A combined and processed DataFrame if successful,
                                 otherwise None.
  """
  # Define the lists used in the original code
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
              'SonBase',]

  # Mapping function (assuming it's defined elsewhere or defined here)
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
  try:
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

    data = response.json()
    if data['success']:
        packages = data['result']['results']
        dfOpendataSwiss = pd.DataFrame(packages)
    else:
        print("API request was not successful.")
        print(data.get('error', 'No error message provided.'))
        return None
  except requests.exceptions.RequestException as e:
      print(f"Error fetching data from opendata.swiss: {e}")
      return None

  dfOpendataSwiss = dfOpendataSwiss[['keywords', 'title','description', 'modified']]
  dfOpendataSwiss['description'] = dfOpendataSwiss['description'].apply(lambda x: x['de'] if isinstance(x, dict) and 'de' in x else None)
  dfOpendataSwiss['title'] = dfOpendataSwiss['title'].apply(lambda x: x['de'] if isinstance(x, dict) and 'de' in x else None)
  dfOpendataSwiss['Typ'] = 'Daten'
  dfOpendataSwiss['Typ'] = dfOpendataSwiss.apply(lambda row: 'Geodatenmodell' if isinstance(row['title'], str) and 'Geodatenmodell' in row['title'] else row['Typ'], axis=1)
  dfOpendataSwiss['Typ'] = dfOpendataSwiss.apply(
      lambda row: 'Monitoring' if any(word in str(row['title']) or word in str(row['description']) for word in Monitoring) else row['Typ'],
      axis=1
  )

  # Statistiken und Indikatoren lesen
  urlexcel = 'https://uvek-gis.admin.ch/BAFU/umweltdaten/opendata.swiss/StatistikenIndikatoren.xlsx'
  try:
    dfStatistikenIndikatoren = pd.read_excel(urlexcel, engine="openpyxl")
  except Exception as e:
      print(f"Error reading Excel file: {e}")
      return None



df_combined_data = prepare_bafu_data()
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


# 1. Install ngrok:
# !pip install pyngrok

# 2. Import and authenticate (optional, but good practice for persistent tunnels):
# from pyngrok import ngrok
# ngrok.set_auth_token("YOUR_NGROK_AUTHTOKEN") # Get your token from ngrok.com

# 3. Save the code above as a Python file (e.g., app.py) in your Colab environment.
#    You can do this by clicking File > New > Python 3 notebook, then saving the cell
#    content as a file.

# 4. Run the Streamlit app using !streamlit run:
# !streamlit run app.py &>/dev/null&

# 5. Start ngrok to expose the Streamlit port (default is 8501):
# public_url = ngrok.connect(port='8501')
# public_url

# This will print a public URL that you can click to access your Streamlit app.
# The `&>/dev/null&` sends the Streamlit output to null and runs it in the background
# so your Colab notebook doesn't get blocked. You can monitor the Streamlit process
# with `!pgrep streamlit`. To stop it, use `!pkill streamlit`.

