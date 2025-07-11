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

# Search field
search_query = st.text_input("Suche nach Titel oder Beschreibung:")

# Filters
st.sidebar.header("Filter")
selected_keyword = st.sidebar.selectbox("Keyword", ['Alle'] + Thema)
selected_type = st.sidebar.selectbox("Typ", ['Alle'] + Datentyp)

# Apply filters
filtered_df = dfCombined.copy()

if selected_keyword != 'Alle':
    mapped_keyword = map_options(selected_keyword)
    if mapped_keyword:
        # Filter rows where the mapped_keyword is in the list of keywords
        filtered_df = filtered_df[filtered_df['keywords'].apply(lambda x: mapped_keyword in x if isinstance(x, list) else False)]
    else:
        # If the keyword doesn't have a mapping, it won't match anything from opendata.swiss.
        # We might need to consider how keywords in the Excel file are handled if they don't map.
        # For now, this will likely filter out items from opendata.swiss without a matching keyword.
        pass # Add logic if needed for handling unmapped keywords from Excel

if selected_type != 'Alle':
    filtered_df = filtered_df[filtered_df['Typ'] == selected_type]

# Apply search query
if search_query:
    filtered_df = filtered_df[
        filtered_df['title'].str.contains(search_query, case=False, na=False) |
        filtered_df['description'].str.contains(search_query, case=False, na=False)
    ]

# Display results
if not filtered_df.empty:
    st.subheader("Ergebnisse:")

    # Define color mapping for Type (customize as needed)
    type_colors = {
        'Daten': '#1f77b4',        # blue
        'Indikator': '#ff7f0e',    # orange
        'Statistik': '#2ca02c',    # green
        'Geodaten': '#d62728',     # red
        'Geodatenmodell': '#9467bd', # purple
        'Monitoring': '#8c564b'     # brown
    }

    # Define color mapping for Keywords (customize as needed, perhaps using a simple hash or cycle)
    # For simplicity, let's use a fixed set of colors and cycle through them
    keyword_color_palette = ['#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5', '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5']
    keyword_color_map = {}
    for i, keyword in enumerate(Thema):
        keyword_color_map[map_options(keyword)] = keyword_color_palette[i % len(keyword_color_palette)]


    for index, row in filtered_df.iterrows():
        with st.expander(row['title']):
            # Display Title (already in the expander title)
            st.write(f"**Titel:** {row['title']}")

            # Display Type as a colored button/badge
            item_type = row['Typ'] if pd.notna(row['Typ']) else 'Unbekannt'
            type_color = type_colors.get(item_type, '#7f7f7f') # Default to grey if type not in map
            st.markdown(
                f"""
                <span style='
                    display: inline-block;
                    padding: 5px 10px;
                    margin-right: 5px;
                    border-radius: 15px;
                    background-color: {type_color};
                    color: white;
                    font-weight: bold;
                    font-size: 0.9em;
                '>
                    {item_type}
                </span>
                """,
                unsafe_allow_html=True
            )

            # Display Keywords as colored buttons/badges
            keywords_list = row['keywords'] if isinstance(row['keywords'], list) else []
            if keywords_list:
                for keyword in keywords_list:
                    original_keyword = next((k for k, v in map_options('').items() if v == keyword), keyword) # Try to map back to original theme name
                    keyword_color = keyword_color_map.get(keyword, '#d62728') # Default to red if mapped keyword not in color map
                    st.markdown(
                        f"""
                        <span style='
                            display: inline-block;
                            padding: 5px 10px;
                            margin-right: 5px;
                            margin-bottom: 5px;
                            border-radius: 15px;
                            background-color: {keyword_color};
                            color: white;
                            font-weight: bold;
                            font-size: 0.9em;
                        '>
                            {original_keyword}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

            # Display Description and Modified Date
            st.write(f"**Beschreibung:** {row['description'] if pd.notna(row['description']) else 'Keine Beschreibung vorhanden'}")
            st.write(f"**Zuletzt geändert:** {row['modified'] if pd.notna(row['modified']) else 'Datum unbekannt'}")

else:
    st.info("Keine Ergebnisse gefunden.")

# --- How to run in Colab ---
# To run this Streamlit app in Google Colab, you need to use a tool like ngrok
# because Streamlit runs a local web server.

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

