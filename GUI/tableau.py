from tkinter import ttk


class TableauResultatFrame(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Proposition panneau solaire + batterie")

        self.tree = ttk.Treeview(
            self,
            columns=("metrique", "valeur"),
            show="headings",
            height=12,
        )
        self.tree.heading("metrique", text="Métrique")
        self.tree.heading("valeur", text="Valeur")
        self.tree.column("metrique", width=260, anchor="w")
        self.tree.column("valeur", width=220, anchor="e")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def afficher_resultats(self, resultats: dict):
        for item in self.tree.get_children():
            self.tree.delete(item)

        mapping = [
            ("Consommation 24h", f"{resultats['consommation_24h_wh']} Wh"),
            ("Panneau recommandé", f"{resultats['puissance_panneau_recommandee_w']} W"),
            ("Batterie recommandée", f"{resultats['capacite_batterie_recommandee_wh']} Wh"),
        ]

        for metrique, valeur in mapping:
            self.tree.insert("", "end", values=(metrique, valeur))
