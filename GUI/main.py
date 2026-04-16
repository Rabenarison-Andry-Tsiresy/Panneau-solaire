import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from GUI.liste_appareil import ListeAppareilFrame
from GUI.tableau import TableauResultatFrame
from models.appareil import Appareil
from utils.CalculFonction import CalculFonction
from utils.Databaseconnection import DatabaseConnection


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dimensionnement solaire")
        self.geometry("980x620")

        self.calculateur = CalculFonction()
        self.db = DatabaseConnection()

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.liste_frame = ListeAppareilFrame(self)
        self.liste_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tableau_frame = TableauResultatFrame(self)
        self.tableau_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

        footer = ttk.Frame(self)
        footer.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        ttk.Button(footer, text="Calculer proposition", command=self.calculer).pack(side=tk.LEFT)
        ttk.Button(footer, text="Charger DB", command=self.charger_db).pack(side=tk.LEFT, padx=6)
        ttk.Button(footer, text="Sauvegarder DB", command=self.sauvegarder_db).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Prêt")
        ttk.Label(footer, textvariable=self.status_var).pack(side=tk.RIGHT)

    def calculer(self):
        appareils = self.liste_frame.get_appareils()
        if not appareils:
            messagebox.showwarning("Aucun appareil", "Ajoutez au moins un appareil")
            return

        resultats = self.calculateur.estimer(appareils)
        self.tableau_frame.afficher_resultats(resultats)
        self.status_var.set("Calcul terminé")

    def charger_db(self):
        appareils, erreur = Appareil.charger_depuis_db(self.db)
        if erreur:
            self.status_var.set("Erreur DB")
            messagebox.showerror("DB", erreur)
            return

        self.liste_frame.set_appareils(appareils)
        self.status_var.set(f"{len(appareils)} appareils chargés")

    def sauvegarder_db(self):
        appareils = self.liste_frame.get_appareils()
        ok, message = Appareil.sauvegarder_dans_db(self.db, appareils)
        if ok:
            self.status_var.set("Sauvegarde DB OK")
            messagebox.showinfo("DB", message)
        else:
            self.status_var.set("Erreur DB")
            messagebox.showerror("DB", message)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
