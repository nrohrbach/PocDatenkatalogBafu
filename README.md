# Proof of Concept Datenkatalog BAFU für neue Webseite auf Livingdocs
Auf der BAFU Webseite sollen künftig alle Daten, Indikatoren, Statistiken und Geodatenmodelle über einen zentralen Katalog gefunden werden. Die Inhalte des Katalogs stammen aus der API von opendata.swiss und von anderen Quellen.

## Woher stammen die Daten
- Alle Einträge von opendata.swiss werden über das API abgefragt
- Die Indikatoren stammen aus der Tabelle aus folgender Webseite: https://www.bafu.admin.ch/bafu/de/home/zustand/indikatoren.html/
- Die Statistiken wurden gemäss Statistikverordnung manuell erfasst: https://www.bfs.admin.ch/asset/de/30106083
- Daten vom Typ "Daten von Webseite" stammen aus dem Webseiten Scraping von Patrick. Berücksichtigt wurden nur Excel-Dateien.
- Die Geodatenmodelle stammen aus der BAFU-Webseite. Siehe: https://github.com/nrohrbach/PocDatenkatalogBafu/tree/main/geodatenmodelle
