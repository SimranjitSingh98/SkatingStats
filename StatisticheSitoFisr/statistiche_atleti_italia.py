# -*- coding: utf-8 -*-
"""Statistiche_Atleti_Italia.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1hU0m8-jiQuu-CtU3lyKfvg0T_5HqaTDF

Questo codice effettua le richieste alla pagina https://www.fisr.info/attivita/corsa_risultati.php per scaricare tutti i dati dalla sezione "attività nazionale". Successivamente crea una tabella per ciascuna categoria, dove le righe rappresentano gli atleti e le colonne rappresentano le gare disputate in tutti i campionati. Ogni cella rappresenta la posizione di quell'atleta a quella gara. Se l'atleta non ha partecipato a quella gara il valore sarà NP.

Istruzioni: eseguire la cella sottostante, aspettare che vengano estratti tutti i dati delle gare e successivamente tramite i bottoni selezionare la categoria che si vuole visualizzare. In fondo alla tabella è possibile tornare indietro per selezionare le altre categorie

Come risultato abbiamo un Dataframe contenente tutti gli atleti e tutte le gare,
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
from tqdm import tqdm  # Barra di progresso
import ipywidgets as widgets
from IPython.display import display, clear_output

# DataFrame globale per memorizzare i dati degli atleti
df_all_data = pd.DataFrame(columns=['Nome Atleta', 'Categoria'])

# Lista per memorizzare le informazioni delle gare
gare = []

# Funzione per recuperare la pagina HTML
def get_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        print(f"Errore nel recupero della pagina: {response.status_code}")
    except requests.RequestException as e:
        print(f"Errore nella richiesta: {e}")
    return None

# Funzione per aggiungere una gara alla lista
def aggiungi_gara(nome_campionato, nome_gara, categoria, url):
    gare.append({
        "nome_campionato": nome_campionato,
        "nome_gara": nome_gara,
        "categoria": categoria,
        "url": url
    })

# Funzione per estrarre i link delle categorie
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

# Funzione per estrarre i campionati e avviare l'estrazione delle categorie
def estrai_campionati(url):
    html = get_html(url)
    if not html:
        return

    soup = BeautifulSoup(html, 'html.parser')
    gare_section = soup.find('div', id='gare_0')

    if gare_section:
        print("ESTRAZIONE DATI DAI SEGUENTI CAMPIONATI: ")
        for div in gare_section.find_all('div', style=True):
            nome_campionato = div.contents[0].strip()
            link = div.find('a', href=True)
            if link:
                link_url = urljoin(url, link['href'])
                estrai_links_categoria(link_url, nome_campionato)
                print(f"{nome_campionato} : {link_url}")
    else:
        print("Sezione gare non trovata.")

# Funzione per aggiungere un atleta al DataFrame
def aggiungi_atleta(atleta, categoria, campionato, gara, posizione, pettorina, squadra, tempo, punti):
    global df_all_data  # Riferimento alla variabile globale

    # Nome della colonna in base al campionato e alla gara
    colonna_gara = f'{campionato}_{gara}'

    # Se la colonna non esiste, aggiungila al DataFrame
    if colonna_gara not in df_all_data.columns:
        df_all_data[colonna_gara] = None

    # Crea un dizionario con tutte le informazioni relative all'atleta e alla gara
    info_atleta = {
        'classifica': posizione,
        'pettorina': pettorina,
        'squadra': squadra,
        'tempo': tempo,
        'punti': punti
    }

    # Verifica se l'atleta e la categoria esistono già nel DataFrame
    matching_rows = df_all_data[(df_all_data['Nome Atleta'] == atleta) & (df_all_data['Categoria'] == categoria)]

    if not matching_rows.empty:  # Se ci sono righe corrispondenti
        # Atleta esistente, trova l'indice della riga corrispondente
        index = matching_rows.index[0]

        # Inserisce il dizionario nella colonna della gara
        df_all_data.at[index, colonna_gara] = info_atleta
    else:
        # Atleta non esistente, aggiungi una nuova riga con tutte le informazioni
        nuova_riga = pd.Series({
            'Nome Atleta': atleta,
            'Categoria': categoria,
            colonna_gara: info_atleta
        })
        df_all_data = pd.concat([df_all_data, nuova_riga.to_frame().T], ignore_index=True)


# Funzione per estrarre e aggiornare i dati di classifica
def estrai_dati_classifica(url, campionato, gara, categoria):
    html = get_html(url)
    if not html:
        return

    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr')

    if not rows:
        print(f"Nessuna riga trovata per {url}")
        return

    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 8:  # Solo righe con 8 colonne
            posizione = cols[0].text.strip()
            pettorina = cols[1].text.strip()
            nome = cols[2].text.strip()
            squadra = cols[4].text.strip()
            tempo = cols[5].text.strip()
            punti = cols[6].text.strip()


            aggiungi_atleta(nome, categoria, campionato, gara, posizione,pettorina,squadra,tempo,punti)

# Funzione per generare i dati per tutte le gare
def genera_dati_per_gare():
    global df_all_data
    if not gare:
        print("Nessuna gara disponibile.")
        return df_all_data

    print("ESTRAZIONE DATI GARE SINGOLE:")

    # Aggiungi la barra di progresso
    for gara in tqdm(gare, desc="Estrazione dati gare", unit="gara", leave=True, ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {percentage:3.0f}%"):
        # La barra viene aggiornata nella stessa linea
        estrai_dati_classifica(gara['url'], gara['nome_gara'], gara['nome_campionato'], gara['categoria'])

    return df_all_data

# Funzione per visualizzare il DataFrame per una determinata categoria
#QUESTA FUNZIONE MOSTRA TUTTO IL DIZIONARIO NELLE CELLE, LA FUNZIONE DI SOTTO SOLO LA POSIZIONE
#IL DIZIONARIO HA ATTRIBUTI IN PIU COME PETTORINA, SQUADRA, TEMPO, PUNTI ECC
'''def visualizza_categoria(categoria):
    df_categoria = df_all_data[df_all_data['Categoria'] == categoria]
    df_categoria_clean = df_categoria.dropna(axis=1, how='all')
    df_categoria_clean = df_categoria_clean.apply(lambda col: col.fillna('NP').replace('', 'NP'))
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    print(f"DataFrame con solo la categoria '{categoria}'")
    display(df_categoria_clean)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')'''

# Funzione per visualizzare il DataFrame per una determinata categoria
def visualizza_categoria(categoria):
    # Filtra il DataFrame per la categoria desiderata
    df_categoria = df_all_data[df_all_data['Categoria'] == categoria]

    # Funzione per estrarre solo il valore della chiave "classifica" da ogni cella del dizionario
    def estrai_classifica(cell):
        # Verifica se la cella è un dizionario e contiene la chiave 'classifica'
        if isinstance(cell, dict) and 'classifica' in cell:
            return cell['classifica']  # Estrae il valore della chiave "classifica"
        # Controlla se la cella è vuota, None o NaN
        if cell is None or cell != cell:  # La condizione cell != cell identifica i NaN
            return 'NP'
        # Se non è un dizionario con 'classifica' e non è vuoto/None/NaN, ritorna il valore originale
        return cell

    # Applica la funzione `estrai_classifica` a tutte le colonne, se contengono dizionari
    df_categoria_clean = df_categoria.applymap(estrai_classifica)

    # Riempie i valori NaN o celle vuote con 'NP'
    df_categoria_clean = df_categoria_clean.apply(lambda col: col.fillna('NP').replace('', 'NP'))

    # Rimuove le colonne che contengono solo valori 'NP'
    df_categoria_clean = df_categoria_clean.loc[:, (df_categoria_clean != 'NP').any(axis=0)]

    # Imposta le opzioni di visualizzazione per mostrare tutte le righe e colonne
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    # Mostra il DataFrame filtrato
    print(f"DataFrame con solo la categoria '{categoria}'")
    display(df_categoria_clean)

    # Ripristina le impostazioni di visualizzazione
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')

# Funzione per la selezione della categoria
def on_button_click(categoria):
    clear_output(wait=True)
    visualizza_categoria(categoria)
    crea_bottone_indietro()

# Funzione per il bottone di ritorno alla scelta delle categorie
def on_back_button_click(button):
    clear_output(wait=True)
    mostra_bottoni()

# Funzione per mostrare i bottoni di categoria
def mostra_bottoni():
    bottoni = [
        'SENIORES F', 'SENIORES M', 'JUNIORES F', 'JUNIORES M',
        'ALLIEVI F', 'ALLIEVI M', 'RAGAZZI F', 'RAGAZZI M',
        'RAGAZZI 12 F', 'RAGAZZI 12 M', 'ESORDIENTI F', 'ESORDIENTI M',
        'GIOVANISSIMI F', 'GIOVANISSIMI M'
    ]
    button_widgets = []
    for categoria in bottoni:
        button = widgets.Button(description=categoria)
        button.on_click(lambda b, categoria=categoria: on_button_click(categoria))
        button_widgets.append(button)

    back_button = widgets.Button(description="Torna indietro")
    back_button.on_click(on_back_button_click)
    display(widgets.VBox(button_widgets + [back_button]))

# Funzione per creare il bottone "Torna indietro" quando si visualizzano i dati
def crea_bottone_indietro():
    back_button = widgets.Button(description="Torna alla selezione delle categorie")
    back_button.on_click(on_back_button_click)
    display(back_button)

# Inizializzazione: estrazione campionati e generazione dati
url = "https://www.fisr.info/attivita/corsa_risultati.php"
estrai_campionati(url)
genera_dati_per_gare()
print("HO FINITO DI ESTRARRE TUTTI I DATI.")

# Mostra i bottoni per la selezione della categoria
mostra_bottoni()