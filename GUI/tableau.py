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
            ("Consommation jour (6h-19h)", f"{resultats['consommation_jour_wh']} Wh"),
            ("Consommation nuit (19h-6h)", f"{resultats['consommation_nuit_wh']} Wh"),
            ("Pic puissance jour", f"{resultats['pic_puissance_jour_w']} W"),
            ("Pic puissance nuit", f"{resultats['pic_puissance_nuit_w']} W"),
            ("Panneau recommandé", f"{resultats['puissance_panneau_recommandee_w']} W"),
            ("Batterie recommandée", f"{resultats['capacite_batterie_recommandee_wh']} Wh"),
            ("Batterie (12V)", f"{resultats['capacite_batterie_recommandee_ah_12v']} Ah"),
            ("Batterie (24V)", f"{resultats['capacite_batterie_recommandee_ah_24v']} Ah"),
        ]

        for metrique, valeur in mapping:
            self.tree.insert("", "end", values=(metrique, valeur))
