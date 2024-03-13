import os
import random
import pygame
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from pypresence import Presence
import time
import asyncio
import json

class LecteurMusique:
    def __init__(self, root):
        self.root = root
        self.root.title("Dium-Song")
        self.repertoire = ""
        self.musiques = []
        self.current_music_index = -1
        self.previous_music_index = -1
        self.volume = 0.5
        self.mode_lecture = "aléatoire"
        self.client_id = ""
        self.nom_musique_en_cours = ""

        self.config_file = "config.json"

        self.lire_config()

        self.label = ttk.Label(root, text="Cliquez sur 'Choisir un répertoire' pour sélectionner le répertoire de musique.", foreground="#333333", font=("Arial", 12))
        self.label.pack(pady=10)

        self.label_client_id = ttk.Label(root, text="Entrez votre Client ID Discord :", foreground="#333333", font=("Arial", 12))
        self.label_client_id.pack(pady=5)
        self.entry_client_id = ttk.Entry(root)
        self.entry_client_id.pack(pady=5)
        self.entry_client_id.insert(0, self.client_id)

        self.bouton_confirmer = ttk.Button(root, text="Confirmer", command=self.confirmer_client_id, style="TButton")
        self.bouton_confirmer.pack(pady=5)

        self.bouton_choisir_repertoire = ttk.Button(root, text="Choisir un répertoire", command=self.choisir_repertoire, style="TButton")
        self.bouton_choisir_repertoire.pack(pady=10)

        self.bouton_jouer = ttk.Button(root, text="Jouer", command=self.jouer_musique, style="TButton")
        self.bouton_jouer.pack(pady=10)
        self.bouton_jouer.config(state=tk.DISABLED)

        self.bouton_suivant = ttk.Button(root, text="Suivant", command=self.jouer_musique_suivante, style="TButton")
        self.bouton_suivant.pack(pady=10)
        self.bouton_suivant.config(state=tk.DISABLED)

        self.bouton_precedent = ttk.Button(root, text="Précédent", command=self.jouer_musique_precedente, style="TButton")
        self.bouton_precedent.pack(pady=10)
        self.bouton_precedent.config(state=tk.DISABLED)

        self.bouton_arreter = ttk.Button(root, text="Arrêter", command=self.arreter_musique, style="TButton")
        self.bouton_arreter.pack(pady=10)
        self.bouton_arreter.config(state=tk.DISABLED)

        self.scale_volume = ttk.Scale(root, from_=0, to=1, command=self.regler_volume, length=200, orient=tk.HORIZONTAL, style="TScale")
        self.scale_volume.set(self.volume)
        self.scale_volume.pack(pady=10)

        self.combo_mode_lecture = ttk.Combobox(root, values=["aléatoire", "répéter"], state="readonly", style="TCombobox")
        self.combo_mode_lecture.current(0 if self.mode_lecture == "aléatoire" else 1)
        self.combo_mode_lecture.pack(pady=10)

        self.init_player()

    def init_player(self):
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)

    def choisir_repertoire(self):
        self.repertoire = filedialog.askdirectory()
        if self.repertoire:
            self.musiques = self.charger_musique()
            if self.musiques:
                self.label.config(text="Répertoire sélectionné. Cliquez sur 'Jouer' pour commencer.", foreground="#333333")
                self.bouton_jouer.config(state=tk.NORMAL)
            else:
                self.label.config(text="Aucune musique trouvée dans le répertoire.", foreground="#FF0000")
        else:
            self.label.config(text="Aucun répertoire sélectionné.", foreground="#FF0000")

    def charger_musique(self):
        musiques = []
        for fichier in os.listdir(self.repertoire):
            if fichier.endswith(".mp3"):
                musiques.append(os.path.join(self.repertoire, fichier))
        return musiques

    def confirmer_client_id(self):
        self.client_id = self.entry_client_id.get()
        self.enregistrer_config()
        if self.client_id:
            self.rpc = Presence(client_id=self.client_id)
            self.rpc.connect()
        else:
            self.label.config(text="Veuillez entrer un Client ID Discord valide.", foreground="#FF0000")

    def jouer_musique(self):
        if self.musiques:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            if self.mode_lecture == "aléatoire":
                self.current_music_index = random.randint(0, len(self.musiques) - 1)
            pygame.mixer.music.load(self.musiques[self.current_music_index])
            pygame.mixer.music.play()
            self.nom_musique_en_cours = os.path.basename(self.musiques[self.current_music_index])
            self.label.config(text=f"En train de jouer : {self.nom_musique_en_cours}", foreground="#333333")
            self.bouton_jouer.config(state=tk.DISABLED)
            self.bouton_suivant.config(state=tk.NORMAL)
            self.bouton_precedent.config(state=tk.NORMAL)
            self.bouton_arreter.config(state=tk.NORMAL)
            self.update_discord_status("Musique en cours de lecture")

    def jouer_musique_suivante(self):
        if self.musiques:
            self.previous_music_index = self.current_music_index
            pygame.mixer.music.stop()
            if self.mode_lecture == "aléatoire":
                self.current_music_index = random.randint(0, len(self.musiques) - 1)
            else:
                self.current_music_index = (self.current_music_index + 1) % len(self.musiques)
            pygame.mixer.music.load(self.musiques[self.current_music_index])
            pygame.mixer.music.play()
            self.nom_musique_en_cours = os.path.basename(self.musiques[self.current_music_index])
            self.label.config(text=f"En train de jouer : {self.nom_musique_en_cours}", foreground="#333333")
            self.update_discord_status("Musique en cours de lecture")

    def jouer_musique_precedente(self):
        if self.musiques:
            pygame.mixer.music.stop()
            self.current_music_index = self.previous_music_index
            pygame.mixer.music.load(self.musiques[self.current_music_index])
            pygame.mixer.music.play()
            self.nom_musique_en_cours = os.path.basename(self.musiques[self.current_music_index])
            self.label.config(text=f"En train de jouer : {self.nom_musique_en_cours}", foreground="#333333")
            self.update_discord_status("Musique en cours de lecture")

    def arreter_musique(self):
        pygame.mixer.music.stop()
        self.label.config(text="Musique arrêtée.", foreground="#333333")
        self.bouton_jouer.config(state=tk.NORMAL)
        self.bouton_suivant.config(state=tk.DISABLED)
        self.bouton_precedent.config(state=tk.DISABLED)
        self.bouton_arreter.config(state=tk.DISABLED)
        self.update_discord_status("Attente de la lecture de musique")

    def regler_volume(self, value):
        self.volume = float(value)
        pygame.mixer.music.set_volume(self.volume)

    def update_discord_status(self, status):
        if hasattr(self, 'rpc'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run_coroutine_threadsafe(self.rpc.update(details=f"En train de jouer {self.nom_musique_en_cours}", state=status), loop)

    def enregistrer_config(self):
        config_data = {
            "client_id": self.client_id,
            "repertoire": self.repertoire,
            "musique_en_cours": self.nom_musique_en_cours,
            "volume": self.volume,
            "mode_lecture": self.mode_lecture
        }
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)

    def lire_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
                self.client_id = config_data.get("client_id", "")
                self.repertoire = config_data.get("repertoire", "")
                self.nom_musique_en_cours = config_data.get("musique_en_cours", "")
                self.volume = config_data.get("volume", 0.5)
                self.mode_lecture = config_data.get("mode_lecture", "aléatoire")

        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                self.jouer_musique_suivante()

def main():
    pygame.init()
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')

    style.configure('TButton', foreground='#FFFFFF', background='#333333', font=('Arial', 12), padding=10, width=15)
    style.map('TButton', foreground=[('pressed', '#FFFFFF'), ('active', '#FFFFFF')], background=[('pressed', '!disabled', '#666666'), ('active', '#666666')])

    style.configure('TLabel', foreground='#333333', font=('Arial', 12))
    style.configure('TEntry', foreground='#333333', font=('Arial', 12))

    lecteur = LecteurMusique(root)
    root.mainloop()

if __name__ == "__main__":
    main()
