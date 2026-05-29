"""Dritarja kryesore e aplikacionit."""
import ctypes
import os
import sys
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


def _ensure_ico_from_png(png_path: str):
    if not _PIL_OK or not os.path.exists(png_path):
        return None

    ico_path = os.path.splitext(png_path)[0] + ".ico"
    try:
        if os.path.exists(ico_path) and os.path.getmtime(ico_path) >= os.path.getmtime(png_path):
            return ico_path

        img = Image.open(png_path).convert("RGBA")
        img.save(ico_path, format="ICO",
                 sizes=[(16, 16), (24, 24), (32, 32), (48, 48),
                        (64, 64), (128, 128), (256, 256)])
        return ico_path
    except Exception:
        return None


def _load_icon_photos(path: str):
    if not _PIL_OK or not os.path.exists(path):
        icon = _load_logo(path, 64)
        return [icon] if icon is not None else []

    photos = []
    try:
        img = Image.open(path).convert("RGBA")
        for size in (256, 128, 64, 48, 32, 24, 16):
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            photos.append(ImageTk.PhotoImage(resized))
    except Exception:
        pass
    return photos


def _set_windows_icons(window, ico_path: str):
    if sys.platform != "win32" or not ico_path or not os.path.exists(ico_path):
        return []

    user32 = ctypes.windll.user32
    image_icon = 1
    lr_loadfromfile = 0x0010
    wm_seticon = 0x0080
    icon_small = 0
    icon_big = 1
    sm_cxicon = 11
    sm_cyicon = 12
    sm_cxsmicon = 49
    sm_cysmicon = 50

    hwnd = window.winfo_id()
    handles = []
    for icon_type, metric_x, metric_y in (
        (icon_small, sm_cxsmicon, sm_cysmicon),
        (icon_big, sm_cxicon, sm_cyicon),
    ):
        handle = user32.LoadImageW(
            None,
            ico_path,
            image_icon,
            user32.GetSystemMetrics(metric_x),
            user32.GetSystemMetrics(metric_y),
            lr_loadfromfile,
        )
        if handle:
            user32.SendMessageW(hwnd, wm_seticon, icon_type, handle)
            handles.append(handle)
    return handles


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1280x800")
        self.configure(bg=COLORS["bg"])
        self.minsize(1280, 800)

        apply_styles(self)

        # Logot — versione të resampluara me Pillow (LANCZOS) për cilësi më të mirë.
        assets = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        logo_path = os.path.join(assets, "logo.png")
        icon_path = os.path.join(assets, "logo_icon.png")
        if not os.path.exists(icon_path):
            icon_path = logo_path
        logo_ico_path = os.path.join(assets, "logo_taskbar.ico")
        if not os.path.exists(logo_ico_path):
            logo_ico_path = _ensure_ico_from_png(icon_path)
        # Logo për header (64 px target, kornizë 80 px e header-it)
        self._logo_header = _load_logo(logo_path, 64)
        # Ikon dritareje (64 px është standard për taskbar/dock)
        self._logo_icons = _load_icon_photos(icon_path)
        icon_applied = False
        if logo_ico_path is not None:
            try:
                self.iconbitmap(default=logo_ico_path)
                icon_applied = sys.platform == "win32"
            except Exception:
                pass
        self._windows_icon_handles = _set_windows_icons(self, logo_ico_path)
        if not icon_applied and self._logo_icons:
            try:
                self.iconphoto(True, *self._logo_icons)
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
