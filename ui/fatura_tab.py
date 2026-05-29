"""Tab për menaxhimin e faturave."""
import tkinter as tk
from tkinter import ttk, messagebox
from models import fatura as m_fatura
from ui.styles import COLORS


class FaturaTab(ttk.Frame):
    COLS = [
        ("fatura_id",     "ID",          50),
        ("data_leshimit", "Data",       110),
        ("klienti",       "Klienti",    180),
        ("nr_dhoma",      "Dhoma",       70),
        ("shuma_neto",    "Neto",       110),
        ("tvsh",          "TVSH",       100),
        ("shuma_totale",  "Totale",     120),
        ("menyra_pagese", "Mënyra",     100),
        ("status_pagese", "Statusi",    120),
    ]

    def __init__(self, parent):
        super().__init__(parent, padding=15)
        self._build()
        self.refresh()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Faturat", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Faturat e qëndrimit dhe pagesat",
                  style="Subtitle.TLabel").pack(side="left", padx=15)
        ttk.Button(header, text="↻ Rifresko",
                   command=self.refresh).pack(side="right")

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=[c[0] for c in self.COLS],
                                  show="headings")
        for c, lbl, w in self.COLS:
            self.tree.heading(c, text=lbl)
            self.tree.column(c, width=w, anchor="w")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda _e: self._shiko_detajet())

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Shiko detajet",
                   command=self._shiko_detajet).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Shëno si E PAGUAR", style="Success.TButton",
                   command=lambda: self._ndrysho_status('E_PAGUAR')).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Anulo faturën", style="Danger.TButton",
                   command=lambda: self._ndrysho_status('E_ANULUAR')).pack(side="left")

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for f in m_fatura.listo():
            self.tree.insert("", "end", values=(
                f["fatura_id"], f["data_leshimit"], f["klienti"], f["nr_dhoma"],
                f"{f['shuma_neto']:.2f} L", f"{f['tvsh']:.2f} L",
                f"{f['shuma_totale']:.2f} L", f["menyra_pagese"], f["status_pagese"]))

    def _selected_id(self):
        sel = self.tree.selection()
        return int(self.tree.item(sel[0], "values")[0]) if sel else None

    def _shiko_detajet(self):
        fid = self._selected_id()
        if not fid:
            messagebox.showwarning("Pa zgjedhje", "Zgjidhni një faturë.")
            return
        f = m_fatura.gjej(fid)
        DetajetFatures(self, f)

    def _ndrysho_status(self, status_i_ri):
        fid = self._selected_id()
        if not fid:
            messagebox.showwarning("Pa zgjedhje", "Zgjidhni një faturë.")
            return
        try:
            m_fatura.ndrysho_status_pageses(fid, status_i_ri)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Gabim", str(e))


class DetajetFatures(tk.Toplevel):
    def __init__(self, parent, fatura):
        super().__init__(parent)
        self.title(f"Faturë #{fatura['fatura_id']}")
        self.configure(bg=COLORS["bg"])
        self.transient(parent)
        self.grab_set()
        self.geometry("550x600")
        self.minsize(550, 600)

        wrap = ttk.Frame(self, padding=25)
        wrap.pack(fill="both", expand=True)

        ttk.Label(wrap, text="HOTEL ADRIATIK", style="Title.TLabel").pack()
        ttk.Label(wrap, text=f"FATURË TATIMORE Nr. {fatura['fatura_id']}",
                  style="Subtitle.TLabel").pack(pady=(0, 15))

        sep = ttk.Separator(wrap, orient="horizontal")
        sep.pack(fill="x", pady=8)

        def row(lbl, val):
            r = ttk.Frame(wrap)
            r.pack(fill="x", pady=2)
            ttk.Label(r, text=lbl, width=22, anchor="w").pack(side="left")
            ttk.Label(r, text=str(val), anchor="w",
                      font=("Helvetica", 10, "bold")).pack(side="left")

        row("Data e lëshimit:", fatura["data_leshimit"])
        row("Klienti:", fatura["klienti"])
        row("Dokument ID:", fatura["dokument_id"])
        row("Dhoma:", f"Nr. {fatura['nr_dhoma']} — {fatura['lloji']}")
        row("Check-in:", fatura["data_check_in"])
        row("Check-out:", fatura["data_check_out"])
        row("Numri i netëve:", fatura["net"])

        ttk.Separator(wrap, orient="horizontal").pack(fill="x", pady=10)

        row("Shuma neto:", f"{fatura['shuma_neto']:.2f} L")
        row("TVSH (20%):", f"{fatura['tvsh']:.2f} L")
        row("TOTAL:", f"{fatura['shuma_totale']:.2f} L")
        row("Mënyra e pagesës:", fatura["menyra_pagese"])
        row("Statusi:", fatura["status_pagese"])

        ttk.Separator(wrap, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(wrap, text="Faleminderit për qëndrimin tuaj!",
                  style="Subtitle.TLabel").pack(pady=10)

        ttk.Button(wrap, text="Mbyll", style="Secondary.TButton",
                   command=self.destroy).pack(pady=10)
