"""Dritarja kryesore e aplikacionit."""
import os
import tkinter as tk
from tkinter import ttk, messagebox

from config import APP_TITLE, APP_VERSION
from db import test_connection
from ui.styles import apply_styles, COLORS
from ui.klient_tab import KlientTab
from ui.dhoma_tab import DhomaTab
from ui.rezervim_tab import RezervimTab
from ui.fatura_tab import FaturaTab
from ui.raporte_tab import RaporteTab

try:
    from PIL import Image, ImageTk
    _PIL_OK = True
except ImportError:
    _PIL_OK = False


def _load_logo(path: str, size: int):
    """Load and high-quality-resize a logo. Returns a PhotoImage or None."""
    if not os.path.exists(path):
        return None
    if _PIL_OK:
        img = Image.open(path).convert("RGBA")
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    # Fallback to tk.PhotoImage (lower quality but no PIL dependency)
    try:
        ph = tk.PhotoImage(file=path)
        factor = max(1, ph.width() // size)
        return ph.subsample(factor, factor)
    except Exception:
        return None


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1280x800")
        self.configure(bg=COLORS["bg"])
        self.minsize(1100, 650)

        apply_styles(self)

        # Logot — versione të resampluara me Pillow (LANCZOS) për cilësi më të mirë.
        assets = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        # Logo për header (64 px target, kornizë 80 px e header-it)
        self._logo_header = _load_logo(os.path.join(assets, "logo.png"), 64)
        # Ikon dritareje (64 px është standard për taskbar/dock)
        self._logo_icon = _load_logo(os.path.join(assets, "logo.png"), 64)
        if self._logo_icon is not None:
            try:
                self.iconphoto(True, self._logo_icon)
            except Exception:
                pass

        # Kontrollo lidhjen
        ok, msg = test_connection()
        if not ok:
            messagebox.showerror(
                "Lidhja me bazën dështoi",
                f"Nuk mund të lidhemi me MySQL:\n\n{msg}\n\n"
                "Sigurohuni që:\n"
                "  • MySQL është duke punuar\n"
                "  • Skema 'hotel_db' është ngarkuar (shihni README.md)\n"
                "  • Kredencialet në config.py janë të sakta")
            self.destroy()
            return

        self._build_header()
        self._build_tabs()
        self._build_statusbar(msg)

    def _build_header(self):
        bar = tk.Frame(self, bg=COLORS["primary"], height=80)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        # Logo në header me cilësi të lartë (LANCZOS resampling përmes Pillow)
        if self._logo_header is not None:
            lbl = tk.Label(bar, image=self._logo_header,
                           bg=COLORS["primary"], bd=0)
            lbl.pack(side="left", padx=15, pady=8)

        ttl = tk.Frame(bar, bg=COLORS["primary"])
        ttl.pack(side="left", padx=10)
        tk.Label(ttl, text="HOTEL ADRIATIK",
                 font=("Helvetica", 18, "bold"),
                 fg=COLORS["white"], bg=COLORS["primary"]).pack(anchor="w")
        tk.Label(ttl, text="Sistemi i Menaxhimit të Rezervimeve",
                 font=("Helvetica", 11),
                 fg="#C7D6EA", bg=COLORS["primary"]).pack(anchor="w")

        tk.Label(bar, text=f"v{APP_VERSION}", font=("Helvetica", 9),
                 fg="#C7D6EA", bg=COLORS["primary"]).pack(side="right", padx=20)

    def _build_tabs(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_klient   = KlientTab(nb)
        self.tab_dhoma    = DhomaTab(nb)
        self.tab_rezervim = RezervimTab(nb, on_change=self._refresh_all)
        self.tab_fatura   = FaturaTab(nb)
        self.tab_raporte  = RaporteTab(nb)

        nb.add(self.tab_klient,   text="  Klientët  ")
        nb.add(self.tab_dhoma,    text="  Dhomat  ")
        nb.add(self.tab_rezervim, text="  Rezervimet  ")
        nb.add(self.tab_fatura,   text="  Faturat  ")
        nb.add(self.tab_raporte,  text="  Raportet  ")

    def _build_statusbar(self, msg):
        sb = tk.Frame(self, bg=COLORS["accent"], height=24)
        sb.pack(side="bottom", fill="x")
        sb.pack_propagate(False)
        tk.Label(sb, text=f"● E lidhur me {msg}", font=("Helvetica", 9),
                 fg=COLORS["success"], bg=COLORS["accent"]).pack(side="left", padx=12)
        tk.Label(sb, text="© 2026 Grupi: Eros Habazaj • Alons Fejzo • Tedi Sina • Tea Sina • Riseld Logu",
                 font=("Helvetica", 9), fg=COLORS["muted"],
                 bg=COLORS["accent"]).pack(side="right", padx=12)

    def _refresh_all(self):
        self.tab_dhoma.refresh()
        self.tab_fatura.refresh()
        self.tab_raporte.refresh()
