import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Definiere die Liste der Optionen
options = ['',
            'Abfall',
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

# Indikatoren nach Thema filtern
def filter_df_by_thema(thema):
    url = "https://www.bafu.admin.ch/bafu/de/home/zustand/indikatoren.html"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
     
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    try:
      html_content = response.content.decode("utf-8")  # Falls `response.content` Byte-Daten enthält.
      soup = BeautifulSoup(html_content, "html.parser")
      table_body = soup.find("table", attrs={"class": "table"})

      if not table_body:
        print("Table not found on the webpage")
        return None

      rows = table_body.find_all("tr")
      data = []
      for row in rows:
          cells = row.find_all("td")
          if len(cells) >= 2:
              thema_cell = cells[0].text.strip()
              indikatorname = cells[1].text.strip()
              link_element = cells[1].find('a')
              href = link_element.get('href') if link_element else None
              data.append({"Thema": thema_cell, "Indikatorname": indikatorname, "Link": "https://www.bafu.admin.ch" + href if href else None})

      df = pd.DataFrame(data)
    except Exception as e:
      print(f"An error occurred while processing the webpage: {e}")
      return None

    # Filter the DataFrame using .isin() for multiple Thema values if needed
    if isinstance(thema, list):
      filtered_df = df[df["Thema"].isin(thema)]
    else:
      filtered_df = df[df["Thema"] == thema]

    return filtered_df







st.title("PoC BAFU Datenkatalog")

st.markdown(
    """
Proof of Concept wie aus der API von opendata.swiss ein Datenkatalog für das BAFU erstellt werden kann.
In folgenden Themen sind bereits Datensätze verschlagwortet:
- Wald
- Boden
- Klima
- Luft

"""
)

st.header("Thema auswählen")
# Erstelle das Auswahlfenster
selected_option = st.selectbox("Wähle ein Thema aus:", options)

# Verwende die map_options Funktion mit der ausgewählten Option
mapped_option = map_options(selected_option)

# Verwende die Abfrage opendata.swiss mit dem gemappten Thema
dfOGD = search_datasets(mapped_option)

#dfIndikator = filter_df_by_thema(selected_option)


#Antwort
st.subheader("OGD Publikationen des BAFU zum Thema opendata.swiss")

# Zeige die gemappte Option an
if mapped_option:
    st.write(f"Das BAFU publiziert folgende Daten zum Thema {selected_option}:")

for index, row in dfOGD.iterrows():
    with st.expander(f"**{row['title']}**"):
        st.write(f"{row['description']}")
        st.markdown(f"[{row['title0']}]({row['url0']})")
        st.markdown(f"[{row['title1']}]({row['url1']})")

#st.subheader("OGD Publikationen des BAFU zum Thema Indikator")
#st.dataframe(dfIndikator)
