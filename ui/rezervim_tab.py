"""Tab për menaxhimin e rezervimeve."""
import tkinter as tk
from datetime import date, timedelta
from tkinter import ttk, messagebox
from models import rezervim as m_rez, klient as m_klient, dhoma as m_dhoma, fatura as m_fatura
from ui.styles import COLORS


class RezervimTab(ttk.Frame):
    COLS = [
        ("rezervim_id",   "ID",          50),
        ("klienti",       "Klienti",    180),
        ("nr_dhoma",      "Dhoma",       80),
        ("lloji",         "Lloji",      120),
        ("data_check_in", "Check-in",   110),
        ("data_check_out","Check-out",  110),
        ("net",           "Netë",        60),
        ("shuma_dhomes",  "Shuma dhomës", 110),
        ("status",        "Statusi",    130),
    ]
    STATUSE = ['TË GJITHA', 'I_REZERVUAR', 'I_REGJISTRUAR', 'I_PERFUNDUAR', 'I_ANULUAR']

    def __init__(self, parent, on_change=None):
        super().__init__(parent, padding=15)
        self.on_change = on_change or (lambda: None)
        self._build()
        self.refresh()

    def _build(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Rezervimet", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="Krijoni dhe menaxhoni rezervimet e dhomave",
                  style="Subtitle.TLabel").pack(side="left", padx=15)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Button(toolbar, text="+ Rezervim i ri",
                   command=self.dialog_shto).pack(side="left", padx=(0, 12))
        ttk.Label(toolbar, text="Filtro sipas statusit:").pack(side="left", padx=(0, 6))
        self.filter_v = tk.StringVar(value='TË GJITHA')
        cb = ttk.Combobox(toolbar, textvariable=self.filter_v, values=self.STATUSE,
                           state="readonly", width=18)
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        ttk.Button(toolbar, text="↻ Rifresko",
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

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Check-in (regjistro)", style="Success.TButton",
                   command=lambda: self._ndrysho_status('I_REGJISTRUAR')).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Check-out + Gjenero faturë",
                   style="Success.TButton",
                   command=self._gjenero_fature).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Anulo", style="Danger.TButton",
                   command=lambda: self._ndrysho_status('I_ANULUAR')).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Fshi", style="Danger.TButton",
                   command=self._fshij).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Shërbime ekstra", style="Secondary.TButton",
                   command=self._sherbime).pack(side="left", padx=(15, 0))

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for r in m_rez.listo(self.filter_v.get()):
            self.tree.insert("", "end", values=(
                r["rezervim_id"], r["klienti"], r["nr_dhoma"], r["lloji"],
                r["data_check_in"], r["data_check_out"], r["net"],
                f"{r['shuma_dhomes']:.2f} L", r["status"]))

    def _selected_id(self):
        sel = self.tree.selection()
        return int(self.tree.item(sel[0], "values")[0]) if sel else None

    def dialog_shto(self):
        RezervimDialog(self, on_save=self._do_shto)

    def _do_shto(self, data):
        try:
            m_rez.shto(**data)
            self.refresh()
            self.on_change()
            return True
        except Exception as e:
            messagebox.showerror("Gabim", str(e))
            return False

    def _ndrysho_status(self, status_i_ri):
        rid = self._selected_id()
        if not rid:
            messagebox.showwarning("Pa zgjedhje", "Zgjidhni një rezervim.")
            return
        try:
            m_rez.ndrysho_status(rid, status_i_ri)
            self.refresh()
            self.on_change()
        except Exception as e:
            messagebox.showerror("Gabim", str(e))

    def _gjenero_fature(self):
        rid = self._selected_id()
        if not rid:
            messagebox.showwarning("Pa zgjedhje", "Zgjidhni një rezervim.")
            return
        try:
            fatura = m_fatura.gjej_per_rezervim(rid)
            if fatura:
                r = m_rez.gjej(rid)
                if r["status"] != 'I_PERFUNDUAR':
                    m_rez.ndrysho_status(rid, 'I_PERFUNDUAR')
                    self.refresh()
                    self.on_change()
                    messagebox.showinfo("Sukses",
                        "Fatura ekziston tashme.\n"
                        "Rezervimi u perfundua me sukses.\n"
                        f"ID e Fatures: {fatura['fatura_id']}")
                else:
                    messagebox.showinfo("Info",
                        "Fatura ekziston tashme dhe rezervimi eshte i perfunduar.\n"
                        f"ID e Fatures: {fatura['fatura_id']}")
                return
        except Exception as e:
            messagebox.showerror("Gabim", str(e))
            return

        r = m_rez.gjej(rid)
        if r["status"] == 'I_PERFUNDUAR':
            messagebox.showinfo("Info", "Rezervimi është i përfunduar tashmë.")
            return
        # zgjidh mënyrën e pagesës
        d = PageseseDialog(self)
        self.wait_window(d)
        if d.menyra is None:
            return
        try:
            fid = m_fatura.gjenero_per_rezervim(rid, d.menyra)
            self.refresh()
            self.on_change()
            messagebox.showinfo("Sukses",
                f"Fatura u gjenerua me sukses.\nID e Faturës: {fid}")
        except Exception as e:
            messagebox.showerror("Gabim", str(e))

    def _fshij(self):
        rid = self._selected_id()
        if not rid:
            return
        if not messagebox.askyesno("Konfirmim", "Fshi rezervimin?"):
            return
        try:
            m_rez.fshij(rid)
            self.refresh()
            self.on_change()
        except Exception as e:
            messagebox.showerror("Gabim", str(e))

    def _sherbime(self):
        rid = self._selected_id()
        if not rid:
            messagebox.showwarning("Pa zgjedhje", "Zgjidhni një rezervim.")
            return
        SherbimDialog(self, rid)


class RezervimDialog(tk.Toplevel):
    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.title("Rezervim i ri")
        self.configure(bg=COLORS["bg"])
        self.transient(parent)
        self.grab_set()
        self.on_save = on_save
        self.resizable(False, False)

        frm = ttk.Frame(self, padding=20)
        frm.pack()

        # Klienti
        ttk.Label(frm, text="Klienti *").grid(row=0, column=0, sticky="w", pady=5)
        self.klientet = m_klient.listo()
        klient_opts = [f"{k['klient_id']} — {k['emer']} {k['mbiemer']} ({k['dokument_id']})"
                        for k in self.klientet]
        self.klient_cb = ttk.Combobox(frm, values=klient_opts,
                                       state="readonly", width=40)
        self.klient_cb.grid(row=0, column=1, pady=5)

        # Datat
        today = date.today()
        ttk.Label(frm, text="Check-in (YYYY-MM-DD) *").grid(row=1, column=0, sticky="w", pady=5)
        self.ci_var = tk.StringVar(value=today.isoformat())
        ttk.Entry(frm, textvariable=self.ci_var, width=40).grid(row=1, column=1, pady=5)

        ttk.Label(frm, text="Check-out (YYYY-MM-DD) *").grid(row=2, column=0, sticky="w", pady=5)
        self.co_var = tk.StringVar(value=(today + timedelta(days=1)).isoformat())
        ttk.Entry(frm, textvariable=self.co_var, width=40).grid(row=2, column=1, pady=5)

        # Buton për të kërkuar dhomat e lira
        ttk.Button(frm, text="🔍 Kërko dhoma të lira", style="Secondary.TButton",
                   command=self._kerko_dhoma).grid(row=3, column=1, sticky="w", pady=(2, 8))

        ttk.Label(frm, text="Dhoma *").grid(row=4, column=0, sticky="w", pady=5)
        self.dhoma_cb = ttk.Combobox(frm, values=[], state="readonly", width=40)
        self.dhoma_cb.grid(row=4, column=1, pady=5)
        self.dhomat = []

        btns = ttk.Frame(frm)
        btns.grid(row=5, column=0, columnspan=2, pady=(15, 0), sticky="e")
        ttk.Button(btns, text="Anulo", style="Secondary.TButton",
                   command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btns, text="Krijo rezervim", command=self._save).pack(side="right")

        self._kerko_dhoma()

    def _kerko_dhoma(self):
        try:
            self.dhomat = m_dhoma.gjej_te_lira_per_periudhe(
                self.ci_var.get(), self.co_var.get())
            opts = [f"{d['dhoma_id']} — Nr.{d['numri']} ({d['lloji']}, "
                    f"{d['cmim_baza']:.0f} L/natë, kap. {d['kapaciteti']})"
                    for d in self.dhomat]
            self.dhoma_cb["values"] = opts
            if not opts:
                messagebox.showinfo("Pa rezultate",
                    "Asnjë dhomë e lirë për këtë periudhë.")
        except Exception as e:
            messagebox.showerror("Gabim", str(e))

    def _save(self):
        try:
            ki = self.klient_cb.current()
            di = self.dhoma_cb.current()
            if ki < 0:
                raise ValueError("Zgjidhni klientin.")
            if di < 0:
                raise ValueError("Zgjidhni dhomën.")
            data = {
                "klient_id": self.klientet[ki]["klient_id"],
                "dhoma_id":  self.dhomat[di]["dhoma_id"],
                "check_in":  self.ci_var.get(),
                "check_out": self.co_var.get(),
            }
            if self.on_save(data):
                self.destroy()
        except Exception as e:
            messagebox.showerror("Gabim", str(e))


class PageseseDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Mënyra e pagesës")
        self.configure(bg=COLORS["bg"])
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.menyra = None

        frm = ttk.Frame(self, padding=20)
        frm.pack()
        ttk.Label(frm, text="Zgjidhni mënyrën e pagesës:",
                  style="Header.TLabel").pack(pady=(0, 10))
        for opt in ['CASH', 'KARTE', 'TRANSFER']:
            ttk.Button(frm, text=opt,
                       command=lambda o=opt: self._zgjedh(o)).pack(fill="x", pady=3)
        ttk.Button(frm, text="Anulo", style="Secondary.TButton",
                   command=self.destroy).pack(fill="x", pady=(10, 0))

    def _zgjedh(self, opt):
        self.menyra = opt
        self.destroy()


class SherbimDialog(tk.Toplevel):
    def __init__(self, parent, rezervim_id):
        super().__init__(parent)
        from models import sherbim as m_sh
        self.title(f"Shërbime — Rezervim #{rezervim_id}")
        self.configure(bg=COLORS["bg"])
        self.transient(parent)
        self.grab_set()
        self.geometry("600x400")
        self.rezervim_id = rezervim_id
        self.m_sh = m_sh

        frm = ttk.Frame(self, padding=15)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Shërbime ekstra", style="Title.TLabel").pack(anchor="w")

        # Shërbimet aktuale
        ttk.Label(frm, text="Të zgjedhura:", style="Header.TLabel").pack(anchor="w", pady=(10, 5))
        self.lst = tk.Listbox(frm, height=6)
        self.lst.pack(fill="x")

        # Shto
        ttk.Label(frm, text="Shto shërbim:", style="Header.TLabel").pack(anchor="w", pady=(15, 5))
        row = ttk.Frame(frm)
        row.pack(fill="x")
        self.sherbimet = m_sh.listo()
        self.cb = ttk.Combobox(row,
            values=[f"{s['sherbim_id']} — {s['emertimi']} ({s['cmimi']:.0f} L)"
                    for s in self.sherbimet], state="readonly", width=35)
        self.cb.pack(side="left", padx=(0, 8))
        ttk.Label(row, text="Sasia:").pack(side="left")
        self.sasia_v = tk.StringVar(value="1")
        ttk.Entry(row, textvariable=self.sasia_v, width=5).pack(side="left", padx=5)
        ttk.Button(row, text="+ Shto", command=self._shto).pack(side="left", padx=8)

        ttk.Button(frm, text="Mbyll", style="Secondary.TButton",
                   command=self.destroy).pack(side="bottom", pady=10)
        self._refresh()

    def _refresh(self):
        self.lst.delete(0, "end")
        from models import rezervim as m_rez
        for rs in m_rez.listo_sherbimet(self.rezervim_id):
            self.lst.insert("end",
                f"{rs['emertimi']} — sasia: {rs['sasia']} × {rs['cmimi']:.0f} L "
                f"= {rs['sasia']*rs['cmimi']:.0f} L")

    def _shto(self):
        try:
            i = self.cb.current()
            if i < 0:
                return
            from models import rezervim as m_rez
            m_rez.shto_sherbim(self.rezervim_id,
                               self.sherbimet[i]["sherbim_id"],
                               int(self.sasia_v.get()))
            self._refresh()
        except Exception as e:
            messagebox.showerror("Gabim", str(e))
