# gui.py
import tkinter as tk
from tkinter import ttk
from estrazione import genera_dati_per_gare, estrai_campionati, df_all_data

def crea_gui():
    root = tk.Tk()
    root.title("Estrattore Atleti")

    # Frame superiore
    frame = tk.Frame(root)
    frame.pack(pady=10)

    # Bottone per estrarre i campionati e visualizzare le categorie
    button = tk.Button(frame, text="Estrai Campionati", command=lambda: estrai_campionati("https://www.fisr.info/attivita/corsa_risultati.php"))
    button.pack(side=tk.LEFT, padx=5)

    # Bottone per visualizzare i dati di tutte le gare
    button_dati = tk.Button(frame, text="Genera Dati Gare", command=genera_dati_per_gare)
    button_dati.pack(side=tk.LEFT, padx=5)

    # Tabella per visualizzare i dati
    cols = list(df_all_data.columns)
    table = ttk.Treeview(root, columns=cols, show='headings')
    for col in cols:
        table.heading(col, text=col)
    table.pack(fill=tk.BOTH, expand=True)

    def mostra_categoria():
        table.delete(*table.get_children())
        for _, row in df_all_data.iterrows():
            table.insert('', 'end', values=row.values)

    button_categoria = tk.Button(root, text="Mostra Categoria", command=mostra_categoria)
    button_categoria.pack(pady=10)

    root.mainloop()
