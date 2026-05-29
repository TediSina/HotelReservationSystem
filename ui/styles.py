"""Central visual styling for the desktop app."""
from tkinter import ttk


COLORS = {
    "bg": "#EEF3F4",
    "surface": "#FFFFFF",
    "surface_alt": "#F7FAF8",
    "panel": "#E5EDF0",
    "primary": "#102A43",
    "primary_light": "#183B56",
    "secondary": "#2F80A8",
    "teal": "#0E7C7B",
    "gold": "#C08A2B",
    "coral": "#C75C48",
    "accent": "#D8E6EA",
    "border": "#C8D6DC",
    "text": "#17212B",
    "muted": "#64727D",
    "success": "#16805D",
    "danger": "#B83F3A",
    "warning": "#B87516",
    "white": "#FFFFFF",
}

FONTS = {
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI Semibold", 10),
    "title": ("Bahnschrift SemiBold", 18),
    "subtitle": ("Segoe UI", 10),
    "header": ("Bahnschrift SemiBold", 12),
    "button": ("Segoe UI Semibold", 10),
    "table": ("Segoe UI", 10),
    "table_heading": ("Segoe UI Semibold", 10),
}

STATUS_TAGS = {
    "I_REZERVUAR": "tag_warning",
    "I_REGJISTRUAR": "tag_success",
    "I_PERFUNDUAR": "tag_muted",
    "I_ANULUAR": "tag_danger",
    "E_LIRE": "tag_success",
    "E_ZENE": "tag_warning",
    "MIREMBAJTJE": "tag_danger",
    "E_PAGUAR": "tag_success",
    "E_PAPAGUAR": "tag_warning",
    "E_ANULUAR": "tag_danger",
}


def apply_styles(root):
    """Configure ttk styles for a more refined operations UI."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        ".",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=FONTS["body"],
        borderwidth=0,
        relief="flat",
    )

    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Surface.TFrame", background=COLORS["surface"], relief="flat")
    style.configure("Toolbar.TFrame", background=COLORS["panel"], relief="flat")
    style.configure("Dialog.TFrame", background=COLORS["bg"], relief="flat")

    style.configure("TNotebook", background=COLORS["bg"], borderwidth=0, tabmargins=(0, 0, 0, 0))
    style.configure(
        "TNotebook.Tab",
        padding=(22, 13),
        font=FONTS["button"],
        background=COLORS["panel"],
        foreground=COLORS["primary"],
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[
            ("selected", COLORS["primary"]),
            ("active", COLORS["accent"]),
        ],
        foreground=[
            ("selected", COLORS["white"]),
            ("active", COLORS["primary"]),
        ],
    )

    style.configure(
        "TButton",
        padding=(14, 9),
        font=FONTS["button"],
        background=COLORS["primary"],
        foreground=COLORS["white"],
        borderwidth=0,
        focusthickness=0,
    )
    style.map(
        "TButton",
        background=[
            ("pressed", COLORS["primary_light"]),
            ("active", COLORS["secondary"]),
            ("disabled", COLORS["border"]),
        ],
        foreground=[("disabled", COLORS["muted"])],
    )

    style.configure("Secondary.TButton", background=COLORS["panel"], foreground=COLORS["primary"])
    style.map(
        "Secondary.TButton",
        background=[
            ("pressed", COLORS["accent"]),
            ("active", COLORS["secondary"]),
            ("disabled", COLORS["border"]),
        ],
        foreground=[("active", COLORS["white"]), ("disabled", COLORS["muted"])],
    )

    style.configure("Danger.TButton", background=COLORS["danger"], foreground=COLORS["white"])
    style.map("Danger.TButton", background=[("pressed", "#8F2E2A"), ("active", COLORS["coral"])])

    style.configure("Success.TButton", background=COLORS["teal"], foreground=COLORS["white"])
    style.map("Success.TButton", background=[("pressed", "#0A5F5E"), ("active", "#11928F")])

    style.configure("Title.TLabel", font=FONTS["title"], foreground=COLORS["primary"], background=COLORS["bg"])
    style.configure("Subtitle.TLabel", font=FONTS["subtitle"], foreground=COLORS["muted"], background=COLORS["bg"])
    style.configure("Header.TLabel", font=FONTS["header"], foreground=COLORS["primary"], background=COLORS["bg"])
    style.configure("Toolbar.TLabel", font=FONTS["body_bold"], foreground=COLORS["primary"], background=COLORS["panel"])
    style.configure("SurfaceTitle.TLabel", font=FONTS["title"], foreground=COLORS["primary"], background=COLORS["surface"])
    style.configure("SurfaceSubtitle.TLabel", font=FONTS["subtitle"], foreground=COLORS["muted"], background=COLORS["surface"])
    style.configure("SurfaceHeader.TLabel", font=FONTS["header"], foreground=COLORS["primary"], background=COLORS["surface"])

    style.configure(
        "TEntry",
        padding=(9, 7),
        relief="flat",
        fieldbackground=COLORS["surface"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
    )
    style.configure(
        "TCombobox",
        padding=(9, 7),
        fieldbackground=COLORS["surface"],
        background=COLORS["surface"],
        bordercolor=COLORS["border"],
        arrowcolor=COLORS["primary"],
    )

    style.configure(
        "Treeview",
        rowheight=34,
        font=FONTS["table"],
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        font=FONTS["table_heading"],
        background=COLORS["primary"],
        foreground=COLORS["white"],
        borderwidth=0,
        padding=(8, 8),
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["secondary"])],
        foreground=[("selected", COLORS["white"])],
    )

    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["panel"],
        troughcolor=COLORS["bg"],
        arrowcolor=COLORS["primary"],
        bordercolor=COLORS["bg"],
    )

    style.configure(
        "TLabelframe",
        background=COLORS["surface"],
        borderwidth=1,
        relief="solid",
        bordercolor=COLORS["border"],
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["surface"],
        foreground=COLORS["primary"],
        font=FONTS["header"],
    )

    style.configure("Horizontal.TSeparator", background=COLORS["border"])

    return style


def style_treeview(tree):
    tree.tag_configure("row_even", background=COLORS["surface"])
    tree.tag_configure("row_odd", background=COLORS["surface_alt"])
    tree.tag_configure("tag_success", foreground=COLORS["success"])
    tree.tag_configure("tag_warning", foreground=COLORS["warning"])
    tree.tag_configure("tag_danger", foreground=COLORS["danger"])
    tree.tag_configure("tag_muted", foreground=COLORS["muted"])


def row_tags(index, status=None):
    tags = ["row_even" if index % 2 == 0 else "row_odd"]
    status_tag = STATUS_TAGS.get(status)
    if status_tag:
        tags.append(status_tag)
    return tuple(tags)
