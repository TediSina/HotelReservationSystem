"""Tab për menaxhimin e dhomave dhe llojeve të dhomave."""
import tkinter as tk
from tkinter import ttk, messagebox
from models import dhoma as m_dhoma, lloji_dhomes as m_lloji
from ui.styles import COLORS, row_tags, style_treeview


class DhomaTab(ttk.Frame):
    COLS = [
        ("dhoma_id", "ID",      50),
        ("numri",    "Nr.",     80),
        ("kati",     "Kati",    60),
        ("lloji",    "Lloji",   140),
        ("kapaciteti","Kap.",   60),
        ("cmim_baza","Çmim/Natë", 110),
        ("status",   "Statusi", 120),
    ]

    def __init__(self, parent):
        super().__init__(parent, padding=15)
        self._build()
        self.refresh()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Dhomat", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Inventari i dhomave dhe llojeve",
                  style="Subtitle.TLabel").pack(side="left", padx=15)

        toolbar = ttk.Frame(self, style="Toolbar.TFrame")
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Button(toolbar, text="+ Shto dhomë",
                   command=self.dialog_shto_dhome).pack(side="left", padx=(0, 8))
        ttk.Button(toolbar, text="Llojet e dhomave", style="Secondary.TButton",
                   command=self.dialog_llojet).pack(side="left")
        ttk.Button(toolbar, text="↻ Rifresko",
                   command=self.refresh).pack(side="right")

        tree_frame = ttk.Frame(self, style="Surface.TFrame")
        tree_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=[c[0] for c in self.COLS],
                                  show="headings")
        style_treeview(self.tree)
        for col, lbl, w in self.COLS:
            self.tree.heading(col, text=lbl)
            self.tree.column(col, width=w, anchor="w")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda _e: self.dialog_perditeso())

        actions = ttk.Frame(self, style="Toolbar.TFrame")
        actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Përditëso", style="Secondary.TButton",
                   command=self.dialog_perditeso).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Fshi", style="Danger.TButton",
                   command=self.fshij).pack(side="left")

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for index, d in enumerate(m_dhoma.listo()):
            row = (
                d["dhoma_id"], d["numri"], d["kati"], d["lloji"],
                d["kapaciteti"], f"{d['cmim_baza']:.2f} L", d["status"],
            )
            self.tree.insert("", "end", values=row, tags=row_tags(index, d["status"]))

    def _selected_id(self):
        sel = self.tree.selection()
        return int(self.tree.item(sel[0], "values")[0]) if sel else None

    def dialog_shto_dhome(self):
        DhomaDialog(self, on_save=self._do_shto)

    def _do_shto(self, data):
        try:
            m_dhoma.shto(**data)
            self.refresh()
            return True
        except Exception as e:
            messagebox.showerror("Gabim", str(e))
            return False

    def dialog_perditeso(self):
        did = self._selected_id()
        if not did:
            messagebox.showwarning("Pa zgjedhje", "Zgjidhni një dhomë.")
            return
        d = m_dhoma.gjej(did)
        DhomaDialog(self, on_save=lambda data: self._do_upd(did, data), initial=d)

    def _do_upd(self, did, data):
        try:
            m_dhoma.perditeso(dhoma_id=did, **data)
            self.refresh()
            return True
        except Exception as e:
            messagebox.showerror("Gabim", str(e))
            return False

    def fshij(self):
        did = self._selected_id()
        if not did:
            return
        if not messagebox.askyesno("Konfirmim", "Fshi dhomën?"):
            return
        try:
            m_dhoma.fshij(did)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Gabim", str(e))

    def dialog_llojet(self):
        LlojetDialog(self)


class DhomaDialog(tk.Toplevel):
    STATUSE = ['E_LIRE', 'E_ZENE', 'MIREMBAJTJE']

    def __init__(self, parent, on_save, initial=None):
        super().__init__(parent)
        self.title("Dhomë")
        self.configure(bg=COLORS["bg"])
        self.on_save = on_save
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        frm = ttk.Frame(self, padding=24, style="Dialog.TFrame")
        frm.pack()

        self.numri_v = tk.StringVar(value=(initial or {}).get("numri", ""))
        self.kati_v  = tk.StringVar(value=str((initial or {}).get("kati", 1)))
        self.lloji_v = tk.StringVar()
        self.status_v = tk.StringVar(value=(initial or {}).get("status", "E_LIRE"))

        ttk.Label(frm, text="Numri *").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(frm, textvariable=self.numri_v, width=25).grid(row=0, column=1, pady=5)
        ttk.Label(frm, text="Kati *").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(frm, textvariable=self.kati_v, width=25).grid(row=1, column=1, pady=5)

        self.llojet = m_lloji.listo()
        opts = [f"{l['lloji_id']} — {l['emertimi']} ({l['cmim_baza']:.0f} L)" for l in self.llojet]
        ttk.Label(frm, text="Lloji *").grid(row=2, column=0, sticky="w", pady=5)
        self.lloji_cb = ttk.Combobox(frm, textvariable=self.lloji_v, values=opts,
                                      state="readonly", width=24)
        self.lloji_cb.grid(row=2, column=1, pady=5)
        if initial:
            for i, l in enumerate(self.llojet):
                if l["lloji_id"] == initial.get("lloji_id"):
                    self.lloji_cb.current(i)
                    break

        ttk.Label(frm, text="Statusi").grid(row=3, column=0, sticky="w", pady=5)
        ttk.Combobox(frm, textvariable=self.status_v, values=self.STATUSE,
                     state="readonly", width=24).grid(row=3, column=1, pady=5)

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, pady=(15, 0), sticky="e")
        ttk.Button(btns, text="Anulo", style="Secondary.TButton",
                   command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="Ruaj", command=self._save).pack(side="right")

    def _save(self):
        try:
            idx = self.lloji_cb.current()
            if idx < 0:
                raise ValueError("Zgjidhni një lloj dhome.")
            data = {
                "numri":    self.numri_v.get().strip(),
                "kati":     int(self.kati_v.get()),
                "lloji_id": self.llojet[idx]["lloji_id"],
                "status":   self.status_v.get(),
            }
            if not data["numri"]:
                raise ValueError("Numri është i detyrueshëm.")
            if self.on_save(data):
                self.destroy()
        except Exception as e:
            messagebox.showerror("Gabim", str(e))


class LlojetDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Llojet e dhomave")
        self.configure(bg=COLORS["bg"])
        self.transient(parent)
        self.grab_set()
        self.geometry("700x600")
        self.minsize(700, 600)

        frm = ttk.Frame(self, padding=18, style="Dialog.TFrame")
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Llojet e dhomave", style="Title.TLabel").pack(anchor="w")

        cols = [("lloji_id", "ID", 50), ("emertimi", "Emërtimi", 150),
                ("kapaciteti", "Kap.", 60),
                ("cmim_baza", "Çmim baza", 120),
                ("pershkrim", "Përshkrim", 280)]
        tree_frame = ttk.Frame(frm, style="Surface.TFrame")
        tree_frame.pack(fill="both", expand=True, pady=10)
        self.tree = ttk.Treeview(tree_frame, columns=[c[0] for c in cols],
                                  show="headings")
        style_treeview(self.tree)
        for c, lbl, w in cols:
            self.tree.heading(c, text=lbl)
            self.tree.column(c, width=w, anchor="w")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        actions = ttk.Frame(frm, style="Toolbar.TFrame")
        actions.pack(fill="x", pady=(5, 0))
        ttk.Button(actions, text="+ Shto lloj",
                   command=self._shto).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Fshi", style="Danger.TButton",
                   command=self._fshij).pack(side="left")
        ttk.Button(actions, text="Mbyll", style="Secondary.TButton",
                   command=self.destroy).pack(side="right")
        self._refresh()

    def _refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for index, l in enumerate(m_lloji.listo()):
            self.tree.insert("", "end", values=(
                l["lloji_id"], l["emertimi"], l["kapaciteti"],
                f"{l['cmim_baza']:.2f} L", l["pershkrim"] or ""),
                tags=row_tags(index))

    def _shto(self):
        d = LlojiDialog(self)
        self.wait_window(d)
        self._refresh()

    def _fshij(self):
        sel = self.tree.selection()
        if not sel:
            return
        lid = int(self.tree.item(sel[0], "values")[0])
        if not messagebox.askyesno("Konfirmim", "Fshi llojin?"):
            return
        try:
            m_lloji.fshij(lid)
            self._refresh()
        except Exception as e:
            messagebox.showerror("Gabim", str(e))


class LlojiDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Lloj i ri")
        self.configure(bg=COLORS["bg"])
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        frm = ttk.Frame(self, padding=24, style="Dialog.TFrame")
        frm.pack()

        self.emertimi   = tk.StringVar()
        self.kapaciteti = tk.StringVar(value="2")
        self.cmim_baza  = tk.StringVar()
        self.pershkrim  = tk.StringVar()

        rows = [("Emërtimi *", self.emertimi),
                ("Kapaciteti *", self.kapaciteti),
                ("Çmim baza *", self.cmim_baza),
                ("Përshkrim", self.pershkrim)]
        for i, (lbl, var) in enumerate(rows):
            ttk.Label(frm, text=lbl).grid(row=i, column=0, sticky="w", pady=5,
                                          padx=(0, 12))
            ttk.Entry(frm, textvariable=var, width=30).grid(row=i, column=1, pady=5)

        btns = ttk.Frame(frm)
        btns.grid(row=len(rows), column=0, columnspan=2, pady=(15, 0), sticky="e")
        ttk.Button(btns, text="Anulo", style="Secondary.TButton",
                   command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="Ruaj", command=self._save).pack(side="right")

    def _save(self):
        try:
            m_lloji.shto(
                emertimi=self.emertimi.get().strip(),
                kapaciteti=int(self.kapaciteti.get()),
                cmim_baza=float(self.cmim_baza.get()),
                pershkrim=self.pershkrim.get().strip() or None,
            )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Gabim", str(e))
