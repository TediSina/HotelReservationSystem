"""Tab për menaxhimin e klientëve."""
import tkinter as tk
from tkinter import ttk, messagebox
from models import klient as m_klient
from ui.styles import COLORS, row_tags, style_treeview


class KlientTab(ttk.Frame):
    COLS = [
        ("klient_id",   "ID",        60),
        ("emer",        "Emër",     130),
        ("mbiemer",     "Mbiemër",  130),
        ("dokument_id", "Dokument", 130),
        ("telefon",     "Telefon",  140),
        ("email",       "Email",    220),
        ("kombesia",    "Kombësia", 120),
    ]

    def __init__(self, parent):
        super().__init__(parent, padding=15)
        self._build()
        self.refresh()

    def _build(self):
        # Krye
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Klientët", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Menaxhimi i klientëve të hotelit",
                  style="Subtitle.TLabel").pack(side="left", padx=15)

        # Search bar
        search = ttk.Frame(self, style="Toolbar.TFrame")
        search.pack(fill="x", pady=(0, 10))
        ttk.Label(search, text="Kërko:", style="Toolbar.TLabel").pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        e = ttk.Entry(search, textvariable=self.search_var, width=30)
        e.pack(side="left")
        e.bind("<KeyRelease>", lambda _e: self.refresh())
        ttk.Button(search, text="+ Shto klient",
                   command=self.dialog_shto).pack(side="right")

        # Tabela
        tree_frame = ttk.Frame(self, style="Surface.TFrame")
        tree_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=[c[0] for c in self.COLS],
                                  show="headings", selectmode="browse")
        style_treeview(self.tree)
        for col, lbl, w in self.COLS:
            self.tree.heading(col, text=lbl)
            self.tree.column(col, width=w, anchor="w")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda _e: self.dialog_perditeso())

        # Veprime
        actions = ttk.Frame(self, style="Toolbar.TFrame")
        actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Përditëso", style="Secondary.TButton",
                   command=self.dialog_perditeso).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Fshi", style="Danger.TButton",
                   command=self.fshij).pack(side="left")
        ttk.Button(actions, text="↻ Rifresko",
                   command=self.refresh).pack(side="right")

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for index, k in enumerate(m_klient.listo(self.search_var.get().strip())):
            self.tree.insert("", "end",
                             values=tuple(k.get(c[0], "") or "" for c in self.COLS),
                             tags=row_tags(index))

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def dialog_shto(self):
        KlientDialog(self, on_save=self._do_shto)

    def _do_shto(self, data):
        try:
            m_klient.shto(**data)
            self.refresh()
            messagebox.showinfo("Sukses", "Klienti u shtua me sukses.")
            return True
        except Exception as e:
            messagebox.showerror("Gabim", f"Nuk mund të shtohej klienti:\n{e}")
            return False

    def dialog_perditeso(self):
        kid = self._selected_id()
        if not kid:
            messagebox.showwarning("Pa zgjedhje", "Zgjidhni një klient nga lista.")
            return
        k = m_klient.gjej(kid)
        KlientDialog(self, on_save=lambda d: self._do_perditeso(kid, d), initial=k)

    def _do_perditeso(self, kid, data):
        try:
            m_klient.perditeso(klient_id=kid, **data)
            self.refresh()
            messagebox.showinfo("Sukses", "Klienti u përditësua.")
            return True
        except Exception as e:
            messagebox.showerror("Gabim", str(e))
            return False

    def fshij(self):
        kid = self._selected_id()
        if not kid:
            messagebox.showwarning("Pa zgjedhje", "Zgjidhni një klient.")
            return
        if not messagebox.askyesno("Konfirmim", "A jeni i sigurt për fshirjen?"):
            return
        try:
            m_klient.fshij(kid)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Gabim",
                f"Klienti nuk mund të fshihet (ndoshta ka rezervime):\n{e}")


class KlientDialog(tk.Toplevel):
    def __init__(self, parent, on_save, initial=None):
        super().__init__(parent)
        self.title("Klienti" if initial else "Klient i ri")
        self.configure(bg=COLORS["bg"])
        self.on_save = on_save
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frm = ttk.Frame(self, padding=24, style="Dialog.TFrame")
        frm.pack()

        self.vars = {k: tk.StringVar(value=(initial or {}).get(k, "") or "")
                     for k in ("emer", "mbiemer", "dokument_id",
                              "telefon", "email", "kombesia")}
        labels = [("emer", "Emër *"), ("mbiemer", "Mbiemër *"),
                  ("dokument_id", "Dokument ID *"), ("telefon", "Telefon"),
                  ("email", "Email"), ("kombesia", "Kombësia")]
        for i, (k, lbl) in enumerate(labels):
            ttk.Label(frm, text=lbl).grid(row=i, column=0, sticky="w",
                                          padx=(0, 12), pady=5)
            ttk.Entry(frm, textvariable=self.vars[k], width=35).grid(
                row=i, column=1, sticky="ew", pady=5)
        if not initial:
            self.vars["kombesia"].set("Shqiptare")

        btns = ttk.Frame(frm)
        btns.grid(row=len(labels), column=0, columnspan=2, pady=(15, 0), sticky="e")
        ttk.Button(btns, text="Anulo", style="Secondary.TButton",
                   command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="Ruaj", command=self._save).pack(side="right")

    def _save(self):
        data = {k: v.get().strip() or None for k, v in self.vars.items()}
        if not data["emer"] or not data["mbiemer"] or not data["dokument_id"]:
            messagebox.showwarning("Të dhëna mungojnë",
                "Emri, mbiemri dhe dokumenti janë të detyrueshme.")
            return
        if self.on_save(data):
            self.destroy()
