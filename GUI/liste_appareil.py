import tkinter as tk
from tkinter import ttk, messagebox
from typing import List

from models.appareil import Appareil


class ListeAppareilFrame(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Liste des appareils")

        self.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            self,
            columns=("nom", "debut", "fin", "puissance"),
            show="headings",
            height=12,
        )
        self.tree.heading("nom", text="Appareil")
        self.tree.heading("debut", text="Début")
        self.tree.heading("fin", text="Fin")
        self.tree.heading("puissance", text="Puissance (W)")
        self.tree.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)

        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Nom").grid(row=1, column=0, sticky="w", padx=8)
        ttk.Label(self, text="Début (0-23)").grid(row=1, column=1, sticky="w", padx=8)
        ttk.Label(self, text="Fin (0-23)").grid(row=1, column=2, sticky="w", padx=8)
        ttk.Label(self, text="Puissance W").grid(row=1, column=3, sticky="w", padx=8)

        self.nom_var = tk.StringVar()
        self.debut_var = tk.StringVar()
        self.fin_var = tk.StringVar()
        self.puissance_var = tk.StringVar()

        ttk.Entry(self, textvariable=self.nom_var).grid(row=2, column=0, sticky="ew", padx=8, pady=4)
        ttk.Entry(self, textvariable=self.debut_var, width=8).grid(row=2, column=1, sticky="ew", padx=8, pady=4)
        ttk.Entry(self, textvariable=self.fin_var, width=8).grid(row=2, column=2, sticky="ew", padx=8, pady=4)
        ttk.Entry(self, textvariable=self.puissance_var, width=10).grid(row=2, column=3, sticky="ew", padx=8, pady=4)

        action_row = ttk.Frame(self)
        action_row.grid(row=3, column=0, columnspan=4, sticky="ew", padx=8, pady=8)

        ttk.Button(action_row, text="Ajouter", command=self.ajouter_appareil).pack(side=tk.LEFT)
        ttk.Button(action_row, text="Supprimer sélection", command=self.supprimer_selection).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_row, text="Vider", command=self.vider).pack(side=tk.LEFT)

    def _valider(self):
        nom = self.nom_var.get().strip()
        if not nom:
            raise ValueError("Le nom est obligatoire")

        try:
            heure_debut = int(self.debut_var.get())
            heure_fin = int(self.fin_var.get())
        except Exception:
            raise ValueError("Heure de début/fin doit être un entier")

        if not (0 <= heure_debut <= 23 and 0 <= heure_fin <= 23):
            raise ValueError("Les heures doivent être entre 0 et 23")

        try:
            puissance = float(self.puissance_var.get())
        except Exception:
            raise ValueError("La puissance doit être un nombre")

        if puissance <= 0:
            raise ValueError("La puissance doit être > 0")

        return nom, heure_debut, heure_fin, puissance

    def ajouter_appareil(self):
        try:
            nom, heure_debut, heure_fin, puissance = self._valider()
            self.tree.insert("", tk.END, values=(nom, heure_debut, heure_fin, puissance))
            self.nom_var.set("")
            self.debut_var.set("")
            self.fin_var.set("")
            self.puissance_var.set("")
        except ValueError as exc:
            messagebox.showerror("Entrée invalide", str(exc))

    def supprimer_selection(self):
        for item in self.tree.selection():
            self.tree.delete(item)

    def vider(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def set_appareils(self, appareils: List[Appareil]):
        self.vider()
        for appareil in appareils:
            self.tree.insert(
                "",
                tk.END,
                values=(appareil.nom, appareil.heure_debut, appareil.heure_fin, appareil.consommation),
            )

    def get_appareils(self) -> List[Appareil]:
        appareils: List[Appareil] = []
        for item in self.tree.get_children():
            nom, debut, fin, puissance = self.tree.item(item, "values")
            appareils.append(
                Appareil(
                    nom=str(nom),
                    heure_debut=int(debut),
                    heure_fin=int(fin),
                    consommation=float(puissance),
                )
            )
        return appareils
