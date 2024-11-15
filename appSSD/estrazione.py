# estrazione.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from tqdm import tqdm

# DataFrame globale per memorizzare i dati degli atleti
df_all_data = pd.DataFrame(columns=['Nome Atleta', 'Categoria'])
gare = []  # Lista per memorizzare le informazioni delle gare

def get_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        print(f"Errore nel recupero della pagina: {response.status_code}")
    except requests.RequestException as e:
        print(f"Errore nella richiesta: {e}")
    return None

def aggiungi_gara(nome_campionato, nome_gara, categoria, url):
    gare.append({"nome_campionato": nome_campionato, "nome_gara": nome_gara, "categoria": categoria, "url": url})

def estrai_links_categoria(url, nome_campionato=None):
    html_content = get_html(url)
    if not html_content:
        return
    soup = BeautifulSoup(html_content, 'html.parser')
    categorie = [
        'SENIORES F', 'SENIORES M', 'JUNIORES F', 'JUNIORES M',
        'ALLIEVI F', 'ALLIEVI M', 'RAGAZZI F', 'RAGAZZI M',
        'RAGAZZI 12 F', 'RAGAZZI 12 M', 'ESORDIENTI F', 'ESORDIENTI M',
        'GIOVANISSIMI F', 'GIOVANISSIMI M'
    ]
    for categoria in categorie:
        categoria_element = soup.find(string=categoria)
        if categoria_element:
            ul = categoria_element.find_next('ul')
            if ul:
                for link in ul.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    nome_gara = link.get_text(strip=True)
                    aggiungi_gara(nome_campionato, nome_gara, categoria, full_url)

def estrai_campionati(url):
    html = get_html(url)
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    gare_section = soup.find('div', id='gare_0')
    if gare_section:
        for div in gare_section.find_all('div', style=True):
            nome_campionato = div.contents[0].strip()
            link = div.find('a', href=True)
            if link:
                link_url = urljoin(url, link['href'])
                estrai_links_categoria(link_url, nome_campionato)

def aggiungi_atleta(atleta, categoria, campionato, gara, posizione, pettorina, squadra, tempo, punti):
    global df_all_data
    colonna_gara = f'{campionato}_{gara}'
    if colonna_gara not in df_all_data.columns:
        df_all_data[colonna_gara] = None
    info_atleta = {'classifica': posizione, 'pettorina': pettorina, 'squadra': squadra, 'tempo': tempo, 'punti': punti}
    matching_rows = df_all_data[(df_all_data['Nome Atleta'] == atleta) & (df_all_data['Categoria'] == categoria)]
    if not matching_rows.empty:
        index = matching_rows.index[0]
        df_all_data.at[index, colonna_gara] = info_atleta
    else:
        nuova_riga = pd.Series({'Nome Atleta': atleta, 'Categoria': categoria, colonna_gara: info_atleta})
        df_all_data = pd.concat([df_all_data, nuova_riga.to_frame().T], ignore_index=True)

def estrai_dati_classifica(url, campionato, gara, categoria):
    html = get_html(url)
    if not html:
        return
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 8:
            posizione, pettorina, nome, squadra, tempo, punti = (
                cols[0].text.strip(), cols[1].text.strip(), cols[2].text.strip(), 
                cols[4].text.strip(), cols[5].text.strip(), cols[6].text.strip()
            )
            aggiungi_atleta(nome, categoria, campionato, gara, posizione, pettorina, squadra, tempo, punti)

def genera_dati_per_gare():
    global df_all_data
    for gara in tqdm(gare, desc="Estrazione dati gare", unit="gara"):
        estrai_dati_classifica(gara['url'], gara['nome_gara'], gara['nome_campionato'], gara['categoria'])
    return df_all_data
