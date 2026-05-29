"""Tab për raportet (të ardhurat mujore, shfrytëzimi i dhomave)."""
import tkinter as tk
from tkinter import ttk
from models import fatura as m_fatura
from ui.styles import COLORS


class RaporteTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=15)
        self._build()
        self.refresh()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Raportet", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Analiza e të ardhurave dhe shfrytëzimit të dhomave",
                  style="Subtitle.TLabel").pack(side="left", padx=15)
        ttk.Button(header, text="↻ Rifresko",
                   command=self.refresh).pack(side="right")

        # Të ardhurat mujore
        lf1 = ttk.LabelFrame(self, text="  Të ardhurat mujore  ", padding=10)
        lf1.pack(fill="both", expand=True, pady=(0, 10))
        cols1 = [("muaji", "Muaji", 120),
                 ("nr_fatura", "Nr. fatura", 120),
                 ("neto_total", "Neto total", 150),
                 ("tvsh_total", "TVSH total", 150),
                 ("shuma_totale", "Total i përgjithshëm", 200)]
        self.tree1 = ttk.Treeview(lf1, columns=[c[0] for c in cols1],
                                   show="headings", height=6)
        for c, lbl, w in cols1:
            self.tree1.heading(c, text=lbl)
            self.tree1.column(c, width=w, anchor="w")
        self.tree1.pack(fill="both", expand=True)

        # Shfrytëzimi
        lf2 = ttk.LabelFrame(self, text="  Shfrytëzimi i dhomave  ", padding=10)
        lf2.pack(fill="both", expand=True)
        cols2 = [("numri", "Dhoma", 100),
                 ("lloji", "Lloji", 150),
                 ("nr_rezervimesh", "Nr. rezervimesh", 150),
                 ("net_total", "Netë gjithsej", 150)]
        self.tree2 = ttk.Treeview(lf2, columns=[c[0] for c in cols2],
                                   show="headings", height=8)
        for c, lbl, w in cols2:
            self.tree2.heading(c, text=lbl)
            self.tree2.column(c, width=w, anchor="w")
        self.tree2.pack(fill="both", expand=True)

    def refresh(self):
        for r in self.tree1.get_children():
            self.tree1.delete(r)
        for row in m_fatura.te_ardhurat_mujore():
            self.tree1.insert("", "end", values=(
                row["muaji"], row["nr_fatura"],
                f"{row['neto_total']:.2f} L",
                f"{row['tvsh_total']:.2f} L",
                f"{row['shuma_totale']:.2f} L"))

        for r in self.tree2.get_children():
            self.tree2.delete(r)
        for row in m_fatura.shfrytezimi_dhomave():
            self.tree2.insert("", "end", values=(
                row["numri"], row["lloji"],
                row["nr_rezervimesh"], row["net_total"]))
