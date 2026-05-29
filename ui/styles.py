"""Stilizimi qendror i aplikacionit."""
from tkinter import ttk

# Paleta sipas logos: blu e thellë navy + blu mesatare
COLORS = {
    "bg":        "#F5F7FA",   # sfond i përgjithshëm
    "primary":   "#1B3A6B",   # navy nga logo
    "secondary": "#5B8FCB",   # blu mesatare nga logo
    "accent":    "#E8EEF6",
    "text":      "#1F2937",
    "muted":     "#6B7280",
    "success":   "#16A34A",
    "danger":    "#DC2626",
    "warning":   "#D97706",
    "white":     "#FFFFFF",
}


def apply_styles(root):
    """Konfiguron stilet ttk për aplikacionin."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"],
                    font=("Helvetica", 10))

    # Notebook
    style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(20, 10), font=("Helvetica", 10, "bold"),
                    background=COLORS["accent"], foreground=COLORS["primary"])
    style.map("TNotebook.Tab",
              background=[("selected", COLORS["primary"])],
              foreground=[("selected", COLORS["white"])])

    # Buttons
    style.configure("TButton", padding=(12, 8), font=("Helvetica", 10),
                    background=COLORS["primary"], foreground=COLORS["white"],
                    borderwidth=0)
    style.map("TButton",
              background=[("active", COLORS["secondary"]),
                          ("disabled", COLORS["muted"])])

    style.configure("Secondary.TButton", background=COLORS["accent"],
                    foreground=COLORS["primary"])
    style.map("Secondary.TButton",
              background=[("active", COLORS["secondary"]),
                          ("disabled", COLORS["muted"])],
              foreground=[("active", COLORS["white"])])

    style.configure("Danger.TButton", background=COLORS["danger"],
                    foreground=COLORS["white"])
    style.map("Danger.TButton",
              background=[("active", "#B91C1C")])

    style.configure("Success.TButton", background=COLORS["success"],
                    foreground=COLORS["white"])
    style.map("Success.TButton",
              background=[("active", "#15803D")])

    # Labels
    style.configure("Title.TLabel", font=("Helvetica", 16, "bold"),
                    foreground=COLORS["primary"], background=COLORS["bg"])
    style.configure("Subtitle.TLabel", font=("Helvetica", 11),
                    foreground=COLORS["muted"], background=COLORS["bg"])
    style.configure("Header.TLabel", font=("Helvetica", 12, "bold"),
                    foreground=COLORS["primary"], background=COLORS["bg"])

    # Entry / Combobox
    style.configure("TEntry", padding=6, relief="flat",
                    fieldbackground=COLORS["white"])
    style.configure("TCombobox", padding=6, fieldbackground=COLORS["white"])

    # Treeview
    style.configure("Treeview", rowheight=28, font=("Helvetica", 10),
                    background=COLORS["white"], fieldbackground=COLORS["white"])
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"),
                    background=COLORS["primary"], foreground=COLORS["white"])
    style.map("Treeview", background=[("selected", COLORS["secondary"])],
              foreground=[("selected", COLORS["white"])])

    # LabelFrame
    style.configure("TLabelframe", background=COLORS["bg"],
                    borderwidth=1, relief="solid")
    style.configure("TLabelframe.Label", background=COLORS["bg"],
                    foreground=COLORS["primary"], font=("Helvetica", 11, "bold"))

    return style
