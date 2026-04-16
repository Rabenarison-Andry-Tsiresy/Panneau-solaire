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
        self.tree.heading("debut", text="Début (HH:MM:SS)")
        self.tree.heading("fin", text="Fin (HH:MM:SS)")
        self.tree.heading("puissance", text="Puissance (W)")
        self.tree.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        ttk.Label(self, text="Nom").grid(row=1, column=0, sticky="w", padx=8)
        ttk.Label(self, text="Début (HH:MM:SS)").grid(row=1, column=1, sticky="w", padx=8)
        ttk.Label(self, text="Fin (HH:MM:SS)").grid(row=1, column=2, sticky="w", padx=8)
        ttk.Label(self, text="Puissance W").grid(row=1, column=3, sticky="w", padx=8)

        self.nom_var = tk.StringVar()
        self.debut_h_var = tk.StringVar(value="06")
        self.debut_m_var = tk.StringVar(value="00")
        self.debut_s_var = tk.StringVar(value="00")
        self.fin_h_var = tk.StringVar(value="19")
        self.fin_m_var = tk.StringVar(value="00")
        self.fin_s_var = tk.StringVar(value="00")
        self.puissance_var = tk.StringVar()

        ttk.Entry(self, textvariable=self.nom_var).grid(row=2, column=0, sticky="ew", padx=8, pady=4)

        debut_frame = ttk.Frame(self)
        debut_frame.grid(row=2, column=1, sticky="w", padx=8, pady=4)
        self._build_time_selector(debut_frame, self.debut_h_var, self.debut_m_var, self.debut_s_var)

        fin_frame = ttk.Frame(self)
        fin_frame.grid(row=2, column=2, sticky="w", padx=8, pady=4)
        self._build_time_selector(fin_frame, self.fin_h_var, self.fin_m_var, self.fin_s_var)

        ttk.Entry(self, textvariable=self.puissance_var, width=10).grid(row=2, column=3, sticky="ew", padx=8, pady=4)

        action_row = ttk.Frame(self)
        action_row.grid(row=3, column=0, columnspan=4, sticky="ew", padx=8, pady=8)

        ttk.Button(action_row, text="Ajouter", command=self.ajouter_appareil).pack(side=tk.LEFT)
        ttk.Button(action_row, text="Supprimer sélection", command=self.supprimer_selection).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_row, text="Vider", command=self.vider).pack(side=tk.LEFT)

    def _build_time_selector(self, parent, var_h: tk.StringVar, var_m: tk.StringVar, var_s: tk.StringVar):
        ttk.Spinbox(parent, from_=0, to=23, width=3, textvariable=var_h, format="%02.0f").pack(side=tk.LEFT)
        ttk.Label(parent, text=":").pack(side=tk.LEFT)
        ttk.Spinbox(parent, from_=0, to=59, width=3, textvariable=var_m, format="%02.0f").pack(side=tk.LEFT)
        ttk.Label(parent, text=":").pack(side=tk.LEFT)
        ttk.Spinbox(parent, from_=0, to=59, width=3, textvariable=var_s, format="%02.0f").pack(side=tk.LEFT)

    @staticmethod
    def _time_to_text(var_h: tk.StringVar, var_m: tk.StringVar, var_s: tk.StringVar) -> str:
        return f"{int(var_h.get()):02d}:{int(var_m.get()):02d}:{int(var_s.get()):02d}"

    def _valider(self):
        nom = self.nom_var.get().strip()
        if not nom:
            raise ValueError("Le nom est obligatoire")

        try:
            heure_debut_texte = self._time_to_text(self.debut_h_var, self.debut_m_var, self.debut_s_var)
            heure_fin_texte = self._time_to_text(self.fin_h_var, self.fin_m_var, self.fin_s_var)
            heure_debut = Appareil.parse_hms(heure_debut_texte)
            heure_fin = Appareil.parse_hms(heure_fin_texte)
        except Exception as exc:
            raise ValueError("Heure invalide, utilisez HH:MM:SS") from exc

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
            self.tree.insert(
                "",
                tk.END,
                values=(nom, Appareil.format_hms(heure_debut), Appareil.format_hms(heure_fin), puissance),
            )
            self.nom_var.set("")
            self.debut_h_var.set("06")
            self.debut_m_var.set("00")
            self.debut_s_var.set("00")
            self.fin_h_var.set("19")
            self.fin_m_var.set("00")
            self.fin_s_var.set("00")
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
                values=(
                    appareil.nom,
                    Appareil.format_hms(appareil.heure_debut),
                    Appareil.format_hms(appareil.heure_fin),
                    appareil.consommation,
                ),
            )

    def get_appareils(self) -> List[Appareil]:
        appareils: List[Appareil] = []
        for item in self.tree.get_children():
            nom, debut, fin, puissance = self.tree.item(item, "values")
            appareils.append(
                Appareil(
                    nom=str(nom),
                    heure_debut=Appareil.parse_hms(str(debut)),
                    heure_fin=Appareil.parse_hms(str(fin)),
                    consommation=float(puissance),
                )
            )
        return appareils
