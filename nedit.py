#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════╗
║          N E D I T   —   Premium Text Editor          ║
║   Warm Amber · Charcoal · Refined Minimalist          ║
╚═══════════════════════════════════════════════════════╝

Features:
  • Multi-tab editing
  • Live Find & Replace with regex support
  • Line-number gutter with active-line highlight
  • Positive + negative line filters (stackable)
  • Current-line highlight
  • Word / character / line count live HUD
  • Syntax-aware keyword coloring (Python, JS, plain)
  • Duplicate line, move line up/down, delete line
  • UPPER / lower / Title case transforms
  • Go-to-line dialog
  • Word wrap toggle
  • Font zoom (Ctrl +/-)
  • Dark ↔ Light theme toggle
  • Auto-indent on Enter
  • Trailing-whitespace stripper on save
  • Unsaved-changes guard
  • Open recent files (session memory)
  • Minimal, icon-free toolbar with hover glow
"""

import tkinter as tk
from tkinter import font as tkfont, messagebox, filedialog, simpledialog
import re, os, sys, json

# ══════════════════════════════════════════════════════════════
#  PALETTE
# ══════════════════════════════════════════════════════════════
DARK = {
    "bg":          "#18181A",
    "panel":       "#1E1E22",
    "toolbar":     "#1A1A1E",
    "gutter_bg":   "#16161A",
    "gutter_fg":   "#3A3A50",
    "gutter_cur":  "#C8923A",
    "text_bg":     "#1E1E22",
    "text_fg":     "#E8DCC8",
    "caret":       "#E8A94A",
    "sel_bg":      "#3A2E18",
    "cur_line":    "#232328",
    "border":      "#2A2A32",
    "sep":         "#28282E",
    "accent":      "#E8A94A",
    "accent2":     "#D4884A",
    "dim":         "#4A4A5A",
    "muted":       "#5A5A6A",
    "success":     "#7EC8A0",
    "danger":      "#E87A6A",
    "warning":     "#E8C84A",
    "info":        "#7AB8E8",
    "sb_bg":       "#14141A",
    "sb_fg":       "#4A4A5A",
    "tab_active":  "#1E1E22",
    "tab_inactive":"#161618",
    "tab_border":  "#E8A94A",
    "match_bg":    "#4A3800",
    "cur_match":   "#C8923A",
    "kw":          "#E87AA8",   # keywords  – rose
    "kw2":         "#7AB8E8",   # builtins  – sky
    "kw3":         "#7EC8A0",   # strings   – sage
    "kw4":         "#B8A8E8",   # numbers   – lavender
    "kw5":         "#8A8A9A",   # comments  – slate
    "btn_bg":      "#28282E",
    "btn_hover":   "#34343C",
    "btn_fg":      "#8A8A9A",
    "btn_accent":  "#E8A94A",
    "entry_bg":    "#16161A",
    "entry_fg":    "#E8DCC8",
    "entry_hl":    "#E8A94A",
}
LIGHT = {
    "bg":          "#F5F0E8",
    "panel":       "#FDFAF4",
    "toolbar":     "#F0EAD8",
    "gutter_bg":   "#EDE7D8",
    "gutter_fg":   "#B0A888",
    "gutter_cur":  "#C8923A",
    "text_bg":     "#FDFAF4",
    "text_fg":     "#2A2218",
    "caret":       "#C8923A",
    "sel_bg":      "#F0D898",
    "cur_line":    "#F5EED8",
    "border":      "#D8D0B8",
    "sep":         "#E0D8C8",
    "accent":      "#C8923A",
    "accent2":     "#A87030",
    "dim":         "#B0A888",
    "muted":       "#8A8068",
    "success":     "#4A9A70",
    "danger":      "#C85A4A",
    "warning":     "#C89830",
    "info":        "#3A78B8",
    "sb_bg":       "#EAE4D4",
    "sb_fg":       "#A09878",
    "tab_active":  "#FDFAF4",
    "tab_inactive":"#EDE7D8",
    "tab_border":  "#C8923A",
    "match_bg":    "#F8E4A0",
    "cur_match":   "#F0B840",
    "kw":          "#C8406A",
    "kw2":         "#2878B8",
    "kw3":         "#3A8850",
    "kw4":         "#7858C8",
    "kw5":         "#909080",
    "btn_bg":      "#E8E0C8",
    "btn_hover":   "#D8D0B8",
    "btn_fg":      "#7A7058",
    "btn_accent":  "#C8923A",
    "entry_bg":    "#F0EAD8",
    "entry_fg":    "#2A2218",
    "entry_hl":    "#C8923A",
}

# ══════════════════════════════════════════════════════════════
#  SYNTAX PATTERNS
# ══════════════════════════════════════════════════════════════
SYNTAX = {
    ".py": {
        "kw":  r"\b(def|class|return|import|from|if|elif|else|for|while|try|except|"
               r"finally|with|as|pass|break|continue|lambda|yield|raise|del|global|"
               r"nonlocal|assert|and|or|not|in|is|True|False|None|async|await)\b",
        "kw2": r"\b(print|len|range|enumerate|zip|map|filter|sorted|list|dict|set|"
               r"tuple|str|int|float|bool|type|isinstance|hasattr|getattr|setattr|"
               r"open|super|self|cls|__init__|__main__)\b",
        "kw3": r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')',
        "kw4": r"\b(\d+\.?\d*[jJ]?)\b",
        "kw5": r"(#[^\n]*)",
    },
    ".js": {
        "kw":  r"\b(function|const|let|var|return|if|else|for|while|class|new|this|"
               r"import|export|default|try|catch|finally|throw|async|await|of|in|"
               r"typeof|instanceof|delete|void|break|continue|switch|case)\b",
        "kw2": r"\b(console|document|window|Array|Object|String|Number|Boolean|Math|"
               r"JSON|Promise|setTimeout|setInterval|undefined|null|true|false)\b",
        "kw3": r'(`[^`]*`|"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\')',
        "kw4": r"\b(\d+\.?\d*)\b",
        "kw5": r"(//[^\n]*|/\*[\s\S]*?\*/)",
    },
}
SYNTAX[".ts"] = SYNTAX[".js"]

# ══════════════════════════════════════════════════════════════
#  FONT PICKER
# ══════════════════════════════════════════════════════════════
MONO_PREF = ["JetBrains Mono", "Cascadia Code", "Fira Code", "Consolas",
             "Menlo", "DejaVu Sans Mono", "Courier New"]
UI_PREF   = ["Segoe UI", "SF Pro Text", "Helvetica Neue", "Helvetica", "TkDefaultFont"]

def best_font(prefs, size, **kw):
    avail = set(tkfont.families())
    for f in prefs:
        if f in avail:
            return tkfont.Font(family=f, size=size, **kw)
    return tkfont.Font(size=size, **kw)

# ══════════════════════════════════════════════════════════════
#  TOOLTIP
# ══════════════════════════════════════════════════════════════
class Tip:
    def __init__(self, w, text):
        self.w, self.text, self.win = w, text, None
        w.bind("<Enter>", self._show, "+")
        w.bind("<Leave>", self._hide, "+")
    def _show(self, e=None):
        x = self.w.winfo_rootx() + 10
        y = self.w.winfo_rooty() + self.w.winfo_height() + 4
        self.win = tw = tk.Toplevel(self.w)
        tw.overrideredirect(True)
        tw.geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.text, bg="#18181A", fg="#C8923A",
                 font=("Consolas", 9), padx=8, pady=3, relief="flat").pack()
    def _hide(self, e=None):
        if self.win: self.win.destroy(); self.win = None

# ══════════════════════════════════════════════════════════════
#  STYLED WIDGETS
# ══════════════════════════════════════════════════════════════
class StyledEntry(tk.Entry):
    def __init__(self, parent, T, **kw):
        super().__init__(parent, bg=T["entry_bg"], fg=T["entry_fg"],
                         insertbackground=T["caret"], relief="flat", bd=0,
                         highlightthickness=1, highlightbackground=T["border"],
                         highlightcolor=T["entry_hl"], **kw)

class PillButton(tk.Label):
    def __init__(self, parent, text, cmd, T, accent=False, danger=False, small=False):
        self.T, self.accent, self.danger = T, accent, danger
        fg = "#18181A" if accent else (T["danger"] if danger else T["btn_fg"])
        bg = T["accent"] if accent else T["btn_bg"]
        fnt = ("Consolas", 9 if small else 10)
        super().__init__(parent, text=text, bg=bg, fg=fg, font=fnt,
                         padx=10 if not small else 7, pady=4 if not small else 2,
                         cursor="hand2", relief="flat")
        self.bind("<Button-1>", lambda e: cmd())
        self.bind("<Enter>",    self._on)
        self.bind("<Leave>",    self._off)
        self._base_bg = bg
        self._base_fg = fg
    def _on(self, e=None):
        self.config(bg=self.T["accent2"] if self.accent else self.T["btn_hover"],
                    fg="#18181A" if self.accent else self.T["btn_accent"])
    def _off(self, e=None):
        self.config(bg=self._base_bg, fg=self._base_fg)

# ══════════════════════════════════════════════════════════════
#  TAB DATA
# ══════════════════════════════════════════════════════════════
class Tab:
    def __init__(self, path=None):
        self.path     = path
        self.saved    = True
        self.original = ""
        self.undo_stack = []
        self.redo_stack = []

# ══════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════
class Nedit:
    RECENT_FILE = os.path.join(os.path.expanduser("~"), ".nedit_recent.json")

    def __init__(self, filename=None):
        self.T         = DARK
        self._theme    = "dark"
        self.font_size = 13
        self.tabs      = []          # list of Tab objects
        self.active    = -1          # current tab index
        self._after_id = None
        self._matches  = []
        self._match_i  = -1
        self._filter_visible  = False
        self._search_visible  = False
        self._recent   = self._load_recent()

        self._build_root()
        self._init_fonts()
        self._build_menu()
        self._build_toolbar()
        self._build_tabs_bar()
        self._build_editor()
        self._build_filter_bar()
        self._build_search_bar()
        self._build_statusbar()
        self._bind_keys()
        self._apply_theme(boot=True)

        if filename and os.path.isfile(filename):
            self._open_path(filename)
        else:
            self._new_tab()

        self.root.mainloop()

    # ── FONTS ──────────────────────────────────────────────────
    def _init_fonts(self):
        self.mono  = best_font(MONO_PREF, self.font_size)
        self.ui    = best_font(UI_PREF,   10)
        self.ui_sm = best_font(UI_PREF,   9)
        self.mono_sm = best_font(MONO_PREF, 9)

    # ── ROOT ───────────────────────────────────────────────────
    def _build_root(self):
        self.root = tk.Tk()
        self.root.title("Nedit")
        self.root.geometry("1280x800")
        self.root.minsize(640, 480)
        self.root.configure(bg=self.T["bg"])

    # ── MENU ───────────────────────────────────────────────────
    def _build_menu(self):
        T = self.T
        def M(parent, **kw):
            return tk.Menu(parent, tearoff=False, bg=T["panel"], fg=T["text_fg"],
                           activebackground=T["accent"], activeforeground="#18181A",
                           relief="flat", **kw)
        mb = M(self.root); self.root.config(menu=mb); self.mb = mb

        fm = M(mb)
        mb.add_cascade(label="File", menu=fm)
        fm.add_command(label="New Tab          Ctrl+T",    command=self._new_tab)
        fm.add_command(label="Open…            Ctrl+O",    command=self._open_dialog)
        fm.add_command(label="Save             Ctrl+S",    command=self._save)
        fm.add_command(label="Save As…         Ctrl+Shift+S", command=self._save_as)
        fm.add_command(label="Close Tab        Ctrl+W",    command=self._close_tab)
        fm.add_separator()
        fm.add_command(label="Quit             Ctrl+Q",    command=self._quit)

        em = M(mb)
        mb.add_cascade(label="Edit", menu=em)
        em.add_command(label="Undo             Ctrl+Z",    command=self._undo)
        em.add_command(label="Redo             Ctrl+Y",    command=self._redo)
        em.add_separator()
        em.add_command(label="Find & Replace   Ctrl+H",    command=self._toggle_search)
        em.add_command(label="Filter Lines     Ctrl+L",    command=self._toggle_filter)
        em.add_command(label="Go to Line…      Ctrl+G",    command=self._goto_line)
        em.add_separator()
        em.add_command(label="Duplicate Line   Ctrl+D",    command=self._dup_line)
        em.add_command(label="Move Line Up     Alt+Up",    command=self._move_up)
        em.add_command(label="Move Line Down   Alt+Down",  command=self._move_down)
        em.add_command(label="Delete Line      Ctrl+K",    command=self._del_line)
        em.add_separator()
        em.add_command(label="UPPERCASE",                  command=lambda: self._case("upper"))
        em.add_command(label="lowercase",                  command=lambda: self._case("lower"))
        em.add_command(label="Title Case",                 command=lambda: self._case("title"))
        em.add_command(label="Strip Trailing Spaces",      command=self._strip_trailing)

        vm = M(mb)
        mb.add_cascade(label="View", menu=vm)
        vm.add_command(label="Toggle Theme      Ctrl+Shift+T", command=self._toggle_theme)
        vm.add_command(label="Zoom In           Ctrl+=",       command=lambda: self._zoom(1))
        vm.add_command(label="Zoom Out          Ctrl+-",       command=lambda: self._zoom(-1))
        vm.add_command(label="Reset Zoom        Ctrl+0",       command=self._zoom_reset)
        vm.add_separator()
        self._wrap_var = tk.BooleanVar(value=True)
        vm.add_checkbutton(label="Word Wrap", variable=self._wrap_var, command=self._toggle_wrap)
        self._ln_var = tk.BooleanVar(value=True)
        vm.add_checkbutton(label="Line Numbers", variable=self._ln_var, command=self._toggle_gutter)

    # ── TOOLBAR ────────────────────────────────────────────────
    def _build_toolbar(self):
        T = self.T
        self.toolbar = tk.Frame(self.root, bg=T["toolbar"], height=46)
        self.toolbar.pack(fill="x", side="top")
        self.toolbar.pack_propagate(False)

        # Logo mark
        logo_f = tk.Frame(self.toolbar, bg=T["toolbar"])
        logo_f.pack(side="left", padx=(18, 4))
        tk.Label(logo_f, text="⬡", font=tkfont.Font(family="Consolas", size=18),
                 bg=T["toolbar"], fg=T["accent"]).pack(side="left")
        tk.Label(logo_f, text="edit", font=tkfont.Font(family="Consolas", size=14),
                 bg=T["toolbar"], fg=T["muted"]).pack(side="left", padx=(1, 0))

        # Separator
        tk.Frame(self.toolbar, bg=T["sep"], width=1).pack(side="left", fill="y", pady=10, padx=12)

        # Action group
        self._tb = {}
        actions = [
            ("New",    "new",   "Ctrl+T  New Tab",    self._new_tab),
            ("Open",   "open",  "Ctrl+O  Open File",  self._open_dialog),
            ("Save",   "save",  "Ctrl+S  Save",       self._save),
            (None,),
            ("Undo",   "undo",  "Ctrl+Z  Undo",       self._undo),
            ("Redo",   "redo",  "Ctrl+Y  Redo",       self._redo),
            (None,),
            ("Find",   "find",  "Ctrl+H  Find & Replace", self._toggle_search),
            ("Filter", "flt",   "Ctrl+L  Filter Lines",   self._toggle_filter),
            ("GoTo",   "goto",  "Ctrl+G  Go to Line",     self._goto_line),
            (None,),
            ("Theme",  "theme", "Ctrl+Shift+T  Toggle Theme", self._toggle_theme),
        ]
        for row in actions:
            if row[0] is None:
                tk.Frame(self.toolbar, bg=T["sep"], width=1).pack(side="left", fill="y", pady=10, padx=8)
                continue
            label, key, tip, cmd = row
            btn = self._tb_btn(self.toolbar, label, cmd)
            Tip(btn, tip)
            self._tb[key] = btn

        # Right side HUD
        hud = tk.Frame(self.toolbar, bg=T["toolbar"])
        hud.pack(side="right", padx=18)
        self.hud_label = tk.Label(hud, text="", font=self.mono_sm,
                                  bg=T["toolbar"], fg=T["dim"])
        self.hud_label.pack()

    def _tb_btn(self, parent, text, cmd):
        T = self.T
        f = tk.Frame(parent, bg=T["toolbar"], cursor="hand2")
        f.pack(side="left", padx=2)
        lbl = tk.Label(f, text=text, font=self.mono_sm,
                       bg=T["toolbar"], fg=T["btn_fg"],
                       padx=10, pady=8, cursor="hand2")
        lbl.pack()
        for w in (f, lbl):
            w.bind("<Button-1>", lambda e, c=cmd: c())
            w.bind("<Enter>",    lambda e, _f=f, _l=lbl: (_f.config(bg=T["btn_hover"]), _l.config(bg=T["btn_hover"], fg=T["btn_accent"])))
            w.bind("<Leave>",    lambda e, _f=f, _l=lbl: (_f.config(bg=T["toolbar"]),  _l.config(bg=T["toolbar"],   fg=T["btn_fg"])))
        return f

    # ── TABS BAR ───────────────────────────────────────────────
    def _build_tabs_bar(self):
        T = self.T
        self.tabs_outer = tk.Frame(self.root, bg=T["bg"], height=36)
        self.tabs_outer.pack(fill="x", side="top")
        self.tabs_outer.pack_propagate(False)
        self.tabs_bar = tk.Frame(self.tabs_outer, bg=T["bg"])
        self.tabs_bar.pack(side="left", fill="both")
        # + button
        plus = tk.Label(self.tabs_outer, text=" + ", font=self.mono_sm,
                        bg=T["bg"], fg=T["dim"], cursor="hand2", pady=6)
        plus.pack(side="left", padx=(0, 8))
        plus.bind("<Button-1>", lambda e: self._new_tab())

    def _redraw_tabs(self):
        T = self.T
        for w in self.tabs_bar.winfo_children():
            w.destroy()
        for i, tab in enumerate(self.tabs):
            name  = (os.path.basename(tab.path) if tab.path else "Untitled")
            dirty = "" if tab.saved else " ●"
            is_active = (i == self.active)
            bg = T["tab_active"] if is_active else T["tab_inactive"]
            fg = T["text_fg"]    if is_active else T["muted"]
            f  = tk.Frame(self.tabs_bar, bg=bg, cursor="hand2")
            f.pack(side="left")
            if is_active:
                tk.Frame(f, bg=T["tab_border"], height=2).pack(fill="x", side="top")
            lbl = tk.Label(f, text=f"  {name}{dirty}  ",
                           font=self.mono_sm, bg=bg, fg=fg, pady=7, cursor="hand2")
            lbl.pack(side="left")
            close = tk.Label(f, text="×", font=self.mono_sm,
                             bg=bg, fg=T["muted"], padx=4, cursor="hand2")
            close.pack(side="left")
            for w in (f, lbl):
                w.bind("<Button-1>", lambda e, idx=i: self._switch_tab(idx))
            close.bind("<Button-1>", lambda e, idx=i: self._close_tab(idx))
            # separator
            tk.Frame(self.tabs_bar, bg=T["sep"], width=1).pack(side="left", fill="y", pady=6)

    # ── EDITOR AREA ────────────────────────────────────────────
    def _build_editor(self):
        T = self.T
        self.editor_frame = tk.Frame(self.root, bg=T["bg"])
        self.editor_frame.pack(expand=True, fill="both")

        # Gutter
        self.gutter = tk.Text(self.editor_frame, width=5, state="disabled",
                              bg=T["gutter_bg"], fg=T["gutter_fg"],
                              font=self.mono, relief="flat", bd=0,
                              padx=8, pady=4, cursor="arrow",
                              selectbackground=T["gutter_bg"])
        self.gutter.pack(side="left", fill="y")
        tk.Frame(self.editor_frame, bg=T["border"], width=1).pack(side="left", fill="y")

        # Scrollbar
        self.vbar = tk.Scrollbar(self.editor_frame, orient="vertical",
                                 bg=T["border"], troughcolor=T["bg"],
                                 activebackground=T["accent"],
                                 relief="flat", width=8, bd=0)
        self.vbar.pack(side="right", fill="y")

        # Text widget
        self.ta = tk.Text(
            self.editor_frame,
            wrap=tk.WORD, font=self.mono,
            bg=T["text_bg"], fg=T["text_fg"],
            insertbackground=T["caret"],
            selectbackground=T["sel_bg"], selectforeground=T["text_fg"],
            relief="flat", bd=0, padx=18, pady=12,
            undo=True, maxundo=200,
            spacing1=2, spacing3=2,
            yscrollcommand=self._scroll_handler,
        )
        self.ta.pack(expand=True, fill="both")
        self.vbar.config(command=self._vscroll)

        # Syntax tags
        self._init_tags()

    def _init_tags(self):
        T = self.T
        self.ta.tag_configure("cur_line",   background=T["cur_line"])
        self.ta.tag_configure("match",      background=T["match_bg"])
        self.ta.tag_configure("cur_match",  background=T["cur_match"], foreground="#18181A")
        self.ta.tag_configure("kw",         foreground=T["kw"])
        self.ta.tag_configure("kw2",        foreground=T["kw2"])
        self.ta.tag_configure("kw3",        foreground=T["kw3"])
        self.ta.tag_configure("kw4",        foreground=T["kw4"])
        self.ta.tag_configure("kw5",        foreground=T["kw5"], font=self.mono)

    # ── FILTER BAR ─────────────────────────────────────────────
    def _build_filter_bar(self):
        T = self.T
        self.filter_bar = tk.Frame(self.root, bg=T["panel"], pady=8)

        top = tk.Frame(self.filter_bar, bg=T["panel"])
        top.pack(fill="x", padx=16, pady=(0, 6))
        tk.Label(top, text="FILTER LINES", font=("Consolas", 8),
                 bg=T["panel"], fg=T["accent"]).pack(side="left")
        PillButton(top, "✕", self._toggle_filter, T, small=True).pack(side="right")

        tk.Frame(self.filter_bar, bg=T["sep"], height=1).pack(fill="x", padx=16, pady=(0, 8))

        r1 = tk.Frame(self.filter_bar, bg=T["panel"])
        r1.pack(fill="x", padx=16, pady=(0, 6))
        tk.Label(r1, text="Include", font=self.ui_sm, bg=T["panel"],
                 fg=T["dim"], width=8, anchor="w").pack(side="left")
        self._fv = tk.StringVar()
        fe = StyledEntry(r1, T, textvariable=self._fv, font=self.mono_sm)
        fe.pack(side="left", expand=True, fill="x", padx=(8, 10))
        fe.bind("<Return>", lambda e: self._apply_filter())
        PillButton(r1, "Apply", self._apply_filter, T, accent=True, small=True).pack(side="left")

        r2 = tk.Frame(self.filter_bar, bg=T["panel"])
        r2.pack(fill="x", padx=16, pady=(0, 6))
        tk.Label(r2, text="Exclude", font=self.ui_sm, bg=T["panel"],
                 fg=T["danger"], width=8, anchor="w").pack(side="left")
        self._nfv = tk.StringVar()
        ne = StyledEntry(r2, T, textvariable=self._nfv, font=self.mono_sm)
        ne.pack(side="left", expand=True, fill="x", padx=(8, 10))
        ne.bind("<Return>", lambda e: self._apply_neg_filter())
        PillButton(r2, "Apply", self._apply_neg_filter, T, danger=True, small=True).pack(side="left")

        br = tk.Frame(self.filter_bar, bg=T["panel"])
        br.pack(fill="x", padx=16, pady=(4, 0))
        PillButton(br, "↺ Reset View", self._reset_filter, T, small=True).pack(side="left", padx=(0, 8))
        PillButton(br, "Clear",        lambda: (self._fv.set(""), self._nfv.set("")), T, small=True).pack(side="left")

    # ── SEARCH BAR ─────────────────────────────────────────────
    def _build_search_bar(self):
        T = self.T
        self.search_bar = tk.Frame(self.root, bg=T["panel"], pady=8)

        top = tk.Frame(self.search_bar, bg=T["panel"])
        top.pack(fill="x", padx=16, pady=(0, 6))
        tk.Label(top, text="FIND & REPLACE", font=("Consolas", 8),
                 bg=T["panel"], fg=T["accent"]).pack(side="left")
        self._match_lbl = tk.Label(top, text="", font=self.ui_sm,
                                   bg=T["panel"], fg=T["warning"])
        self._match_lbl.pack(side="left", padx=14)
        PillButton(top, "✕", self._toggle_search, T, small=True).pack(side="right")

        tk.Frame(self.search_bar, bg=T["sep"], height=1).pack(fill="x", padx=16, pady=(0, 8))

        fr = tk.Frame(self.search_bar, bg=T["panel"])
        fr.pack(fill="x", padx=16, pady=(0, 6))
        tk.Label(fr, text="Find", font=self.ui_sm, bg=T["panel"],
                 fg=T["dim"], width=8, anchor="w").pack(side="left")
        self._sv = tk.StringVar()
        self._se = StyledEntry(fr, T, textvariable=self._sv, font=self.mono_sm)
        self._se.pack(side="left", expand=True, fill="x", padx=(8, 10))
        self._se.bind("<Return>",    lambda e: self._next_match())
        self._se.bind("<KeyRelease>", lambda e: self._live_search())
        PillButton(fr, "◀", self._prev_match, T, small=True).pack(side="left", padx=(0, 4))
        PillButton(fr, "▶", self._next_match, T, accent=True, small=True).pack(side="left")

        opts = tk.Frame(self.search_bar, bg=T["panel"])
        opts.pack(fill="x", padx=90, pady=(0, 6))
        self._case_var  = tk.BooleanVar()
        self._regex_var = tk.BooleanVar()
        self._whole_var = tk.BooleanVar()
        for var, label in ((self._case_var, "Aa"), (self._regex_var, ".*"), (self._whole_var, "\\b")):
            cb = tk.Checkbutton(opts, text=label, variable=var,
                                bg=T["panel"], fg=T["muted"], font=("Consolas", 9),
                                selectcolor=T["entry_bg"], activebackground=T["panel"],
                                command=self._live_search)
            cb.pack(side="left", padx=(0, 12))
            Tip(cb, {"Aa": "Case sensitive", ".*": "Use regex", "\\b": "Whole word"}[label])

        rr = tk.Frame(self.search_bar, bg=T["panel"])
        rr.pack(fill="x", padx=16, pady=(0, 6))
        tk.Label(rr, text="Replace", font=self.ui_sm, bg=T["panel"],
                 fg=T["dim"], width=8, anchor="w").pack(side="left")
        self._rv = tk.StringVar()
        StyledEntry(rr, T, textvariable=self._rv, font=self.mono_sm).pack(
            side="left", expand=True, fill="x", padx=(8, 10))
        PillButton(rr, "One",  self._replace_one, T, small=True).pack(side="left", padx=(0, 4))
        PillButton(rr, "All",  self._replace_all, T, accent=True, small=True).pack(side="left")

    # ── STATUS BAR ─────────────────────────────────────────────
    def _build_statusbar(self):
        T = self.T
        self.sb = tk.Frame(self.root, bg=T["sb_bg"], height=26)
        self.sb.pack(fill="x", side="bottom")
        self.sb.pack_propagate(False)

        self._sb_file = tk.Label(self.sb, text="", font=self.mono_sm,
                                 bg=T["sb_bg"], fg=T["sb_fg"])
        self._sb_file.pack(side="left", padx=(14, 0))

        right = tk.Frame(self.sb, bg=T["sb_bg"])
        right.pack(side="right", padx=14)
        self._sb_sel  = tk.Label(right, text="",          font=self.mono_sm, bg=T["sb_bg"], fg=T["warning"])
        self._sb_sel.pack(side="right", padx=(12, 0))
        self._sb_pos  = tk.Label(right, text="Ln 1, Col 1", font=self.mono_sm, bg=T["sb_bg"], fg=T["sb_fg"])
        self._sb_pos.pack(side="right", padx=(12, 0))
        self._sb_enc  = tk.Label(right, text="UTF-8",     font=self.mono_sm, bg=T["sb_bg"], fg=T["dim"])
        self._sb_enc.pack(side="right", padx=(12, 0))
        self._sb_lang = tk.Label(right, text="Plain",     font=self.mono_sm, bg=T["sb_bg"], fg=T["dim"])
        self._sb_lang.pack(side="right")

    # ── KEY BINDINGS ───────────────────────────────────────────
    def _bind_keys(self):
        ta, r = self.ta, self.root
        ta.bind("<KeyRelease>",    self._on_edit)
        ta.bind("<ButtonRelease>", self._on_edit)
        ta.bind("<Return>",        self._auto_indent, "+")
        r.bind("<Control-t>",      lambda e: self._new_tab())
        r.bind("<Control-o>",      lambda e: self._open_dialog())
        r.bind("<Control-s>",      lambda e: self._save())
        r.bind("<Control-S>",      lambda e: self._save_as())
        r.bind("<Control-w>",      lambda e: self._close_tab())
        r.bind("<Control-q>",      lambda e: self._quit())
        r.bind("<Control-z>",      lambda e: self._undo())
        r.bind("<Control-y>",      lambda e: self._redo())
        r.bind("<Control-h>",      lambda e: self._toggle_search())
        r.bind("<Control-l>",      lambda e: self._toggle_filter())
        r.bind("<Control-g>",      lambda e: self._goto_line())
        r.bind("<Control-d>",      lambda e: self._dup_line())
        r.bind("<Control-k>",      lambda e: self._del_line())
        r.bind("<Alt-Up>",         lambda e: self._move_up())
        r.bind("<Alt-Down>",       lambda e: self._move_down())
        r.bind("<Control-equal>",  lambda e: self._zoom(1))
        r.bind("<Control-minus>",  lambda e: self._zoom(-1))
        r.bind("<Control-0>",      lambda e: self._zoom_reset())
        r.bind("<Control-T>",      lambda e: self._toggle_theme())  # Shift+T
        r.bind("<Escape>",         lambda e: self._close_panels())
        r.bind("<Control-Tab>",    lambda e: self._next_tab())
        r.bind("<Control-Prior>",  lambda e: self._next_tab(-1))

    # ── SCROLL SYNC ────────────────────────────────────────────
    def _scroll_handler(self, *args):
        self.vbar.set(*args)
        self._update_gutter()

    def _vscroll(self, *args):
        self.ta.yview(*args)
        self._update_gutter()

    # ── GUTTER ─────────────────────────────────────────────────
    def _update_gutter(self):
        if not self._ln_var.get(): return
        g = self.gutter
        g.config(state="normal")
        g.delete("1.0", "end")
        idx   = self.ta.index("@0,0")
        cur_r = int(self.ta.index("insert").split(".")[0])
        while True:
            info = self.ta.dlineinfo(idx)
            if info is None: break
            row = int(idx.split(".")[0])
            fg  = self.T["gutter_cur"] if row == cur_r else self.T["gutter_fg"]
            wt  = "bold" if row == cur_r else "normal"
            g.insert("end", f"{row:>4}\n")
            g.tag_add(f"r{row}", f"end-{1+len(str(row))}c", f"end-1c")
            g.tag_configure(f"r{row}", foreground=fg)
            ni = self.ta.index(f"{idx}+1line")
            if ni == idx: break
            idx = ni
        g.config(state="disabled")

    def _toggle_gutter(self):
        if self._ln_var.get():
            self.gutter.pack(side="left", fill="y", before=self.editor_frame.winfo_children()[1])
        else:
            self.gutter.pack_forget()

    # ── SYNTAX HIGHLIGHT ───────────────────────────────────────
    def _highlight_syntax(self):
        tab = self._cur_tab()
        if tab is None: return
        ext = os.path.splitext(tab.path or "")[1].lower() if tab.path else ""
        patterns = SYNTAX.get(ext, {})
        for tag in ("kw", "kw2", "kw3", "kw4", "kw5"):
            self.ta.tag_remove(tag, "1.0", "end")
        content = self.ta.get("1.0", "end-1c")
        # Apply tags in order (comments last to override)
        order = ["kw4", "kw3", "kw2", "kw", "kw5"]
        for tag in order:
            pat = patterns.get(tag)
            if not pat: continue
            for m in re.finditer(pat, content, re.MULTILINE):
                s = self._offset_idx(content, m.start())
                e = self._offset_idx(content, m.end())
                self.ta.tag_add(tag, s, e)

    def _offset_idx(self, content, offset):
        lines = content[:offset].split("\n")
        return f"{len(lines)}.{len(lines[-1])}"

    # ── ON EDIT ────────────────────────────────────────────────
    def _on_edit(self, e=None):
        tab = self._cur_tab()
        if tab:
            current = self.ta.get("1.0", "end-1c")
            tab.saved = (current == tab.original)
            self._redraw_tabs()
        if self._after_id:
            self.root.after_cancel(self._after_id)
        self._after_id = self.root.after(80, self._deferred_update)

    def _deferred_update(self):
        self._update_statusbar()
        self._update_gutter()
        self._update_hud()
        self._highlight_cur_line()
        self._highlight_syntax()

    # ── CURRENT LINE ───────────────────────────────────────────
    def _highlight_cur_line(self):
        self.ta.tag_remove("cur_line", "1.0", "end")
        ln = self.ta.index("insert linestart")
        self.ta.tag_add("cur_line", ln, f"{ln} lineend+1c")

    # ── STATUS / HUD ───────────────────────────────────────────
    def _update_statusbar(self):
        idx  = self.ta.index("insert")
        ln, col = idx.split(".")
        self._sb_pos.config(text=f"Ln {ln}, Col {int(col)+1}")
        try:
            sel = self.ta.get("sel.first", "sel.last")
            self._sb_sel.config(text=f"  {len(sel)} selected")
        except tk.TclError:
            self._sb_sel.config(text="")
        tab = self._cur_tab()
        if tab:
            self._sb_file.config(text=tab.path or "Untitled")
            ext = os.path.splitext(tab.path or "")[1].lstrip(".").upper() or "Plain"
            self._sb_lang.config(text=ext if ext else "Plain")

    def _update_hud(self):
        c = self.ta.get("1.0", "end-1c")
        words = len(c.split()) if c.strip() else 0
        lines = c.count("\n") + 1 if c else 0
        self.hud_label.config(text=f"{words:,}w  {len(c):,}ch  {lines:,}ln")

    # ── THEME ──────────────────────────────────────────────────
    def _toggle_theme(self):
        self._theme = "light" if self._theme == "dark" else "dark"
        self.T = LIGHT if self._theme == "light" else DARK
        self._apply_theme()

    def _apply_theme(self, boot=False):
        T = self.T
        self.root.configure(bg=T["bg"])
        # Editor
        self.ta.configure(bg=T["text_bg"], fg=T["text_fg"],
                          insertbackground=T["caret"],
                          selectbackground=T["sel_bg"])
        self.gutter.configure(bg=T["gutter_bg"], fg=T["gutter_fg"])
        self.editor_frame.configure(bg=T["bg"])
        self.vbar.configure(bg=T["border"], troughcolor=T["bg"], activebackground=T["accent"])
        # Tags
        self._init_tags()
        # Toolbar
        self.toolbar.configure(bg=T["toolbar"])
        self.hud_label.configure(bg=T["toolbar"], fg=T["dim"])
        # Tabs
        self.tabs_outer.configure(bg=T["bg"])
        self.tabs_bar.configure(bg=T["bg"])
        # Status
        self.sb.configure(bg=T["sb_bg"])
        for w in self.sb.winfo_children():
            try: w.configure(bg=T["sb_bg"])
            except: pass
        for attr in ("_sb_file", "_sb_pos", "_sb_enc", "_sb_lang"):
            getattr(self, attr).configure(bg=T["sb_bg"], fg=T["sb_fg"])
        self._sb_sel.configure(bg=T["sb_bg"], fg=T["warning"])
        # Panels (rebuild if visible)
        if not boot:
            was_f = self._filter_visible
            was_s = self._search_visible
            if was_f:
                self.filter_bar.pack_forget(); self._filter_visible = False
            if was_s:
                self.search_bar.pack_forget(); self._search_visible = False
            self.filter_bar.destroy(); self.search_bar.destroy()
            self._build_filter_bar(); self._build_search_bar()
            if was_f: self._toggle_filter()
            if was_s: self._toggle_search()
            self._redraw_tabs()
            self._deferred_update()

    # ── TABS ───────────────────────────────────────────────────
    def _new_tab(self, path=None):
        tab = Tab(path)
        self.tabs.append(tab)
        self._switch_tab(len(self.tabs) - 1)

    def _switch_tab(self, idx):
        if not (0 <= idx < len(self.tabs)): return
        # Save current text into old tab (don't lose edits)
        if 0 <= self.active < len(self.tabs):
            self.tabs[self.active]._text_snapshot = self.ta.get("1.0", "end-1c")
        self.active = idx
        tab = self.tabs[idx]
        self.ta.delete("1.0", "end")
        snapshot = getattr(tab, "_text_snapshot", None)
        if snapshot is not None:
            self.ta.insert("end", snapshot)
        elif tab.path and os.path.isfile(tab.path):
            self._load_path_into_tab(tab)
        self.root.title(f"Nedit — {os.path.basename(tab.path) if tab.path else 'Untitled'}")
        self._redraw_tabs()
        self._deferred_update()

    def _close_tab(self, idx=None):
        if idx is None: idx = self.active
        if not (0 <= idx < len(self.tabs)): return
        tab = self.tabs[idx]
        if not tab.saved:
            if not messagebox.askyesno("Unsaved", f"Close '{os.path.basename(tab.path) or 'Untitled'}' without saving?"):
                return
        self.tabs.pop(idx)
        if not self.tabs:
            self._new_tab()
            return
        self.active = max(0, min(idx, len(self.tabs) - 1))
        self._switch_tab(self.active)

    def _next_tab(self, d=1):
        if self.tabs:
            self._switch_tab((self.active + d) % len(self.tabs))

    def _cur_tab(self):
        if 0 <= self.active < len(self.tabs):
            return self.tabs[self.active]
        return None

    # ── FILE OPS ───────────────────────────────────────────────
    def _open_dialog(self):
        path = filedialog.askopenfilename(
            title="Open",
            filetypes=[("Source / Text", "*.py *.js *.ts *.txt *.md *.json *.yaml *.yml *.csv *.log *.html *.css *.sh"),
                       ("All files", "*.*")])
        if path: self._open_path(path)

    def _open_path(self, path):
        # Reuse existing tab if already open
        for i, t in enumerate(self.tabs):
            if t.path == path:
                self._switch_tab(i); return
        tab = Tab(path)
        self.tabs.append(tab)
        self._switch_tab(len(self.tabs) - 1)
        self._add_recent(path)

    def _load_path_into_tab(self, tab):
        try:
            with open(tab.path, "r", encoding="utf-8", errors="replace") as f:
                tab.original = f.read()
            self.ta.delete("1.0", "end")
            self.ta.insert("end", tab.original)
            tab.saved = True
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _save(self):
        tab = self._cur_tab()
        if tab is None: return
        if tab.path is None:
            self._save_as(); return
        self._write(tab, tab.path)

    def _save_as(self):
        tab = self._cur_tab()
        if tab is None: return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if path:
            self._write(tab, path)
            tab.path = path
            self._add_recent(path)
            self._redraw_tabs()
            self.root.title(f"Nedit — {os.path.basename(path)}")

    def _write(self, tab, path):
        try:
            content = self.ta.get("1.0", "end-1c")
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            tab.original = content
            tab.saved = True
            self._redraw_tabs()
            self._flash(f"Saved  ✓  {os.path.basename(path)}", self.T["success"])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _flash(self, msg, color):
        orig = self._sb_file.cget("text")
        self._sb_file.config(text=f"  {msg}", fg=color)
        self.root.after(2000, lambda: self._sb_file.config(text=orig, fg=self.T["sb_fg"]))

    def _new_tab_cmd(self):
        self._new_tab()

    # ── AUTO INDENT ────────────────────────────────────────────
    def _auto_indent(self, e=None):
        idx    = self.ta.index("insert-1line linestart")
        line   = self.ta.get(idx, f"{idx} lineend")
        indent = len(line) - len(line.lstrip())
        extra  = 0
        if line.rstrip().endswith(":"):   extra = 4   # Python
        if line.rstrip().endswith("{"):   extra = 4   # JS/TS
        self.ta.insert("insert", " " * (indent + extra))
        return "break" if extra else None

    # ── UNDO / REDO ────────────────────────────────────────────
    def _undo(self):
        tab = self._cur_tab()
        if tab and tab.undo_stack:
            tab.redo_stack.append(self.ta.get("1.0", "end-1c"))
            self._set_text(tab.undo_stack.pop())
        else:
            try: self.ta.edit_undo()
            except: pass

    def _redo(self):
        tab = self._cur_tab()
        if tab and tab.redo_stack:
            tab.undo_stack.append(self.ta.get("1.0", "end-1c"))
            self._set_text(tab.redo_stack.pop())
        else:
            try: self.ta.edit_redo()
            except: pass

    def _push_undo(self):
        tab = self._cur_tab()
        if tab:
            tab.undo_stack.append(self.ta.get("1.0", "end-1c"))
            tab.redo_stack.clear()

    # ── EDIT ACTIONS ───────────────────────────────────────────
    def _dup_line(self):
        idx = self.ta.index("insert")
        ls  = self.ta.index(f"{idx} linestart")
        le  = self.ta.index(f"{idx} lineend")
        txt = self.ta.get(ls, le)
        self.ta.insert(le, f"\n{txt}")

    def _move_up(self):
        idx = self.ta.index("insert")
        r   = int(idx.split(".")[0])
        if r <= 1: return
        a = self.ta.get(f"{r}.0",   f"{r}.end")
        b = self.ta.get(f"{r-1}.0", f"{r-1}.end")
        self.ta.delete(f"{r-1}.0", f"{r}.end")
        self.ta.insert(f"{r-1}.0", f"{a}\n{b}")
        self.ta.mark_set("insert", f"{r-1}.{idx.split('.')[1]}")

    def _move_down(self):
        idx   = self.ta.index("insert")
        r     = int(idx.split(".")[0])
        total = int(self.ta.index("end-1c").split(".")[0])
        if r >= total: return
        a = self.ta.get(f"{r}.0",   f"{r}.end")
        b = self.ta.get(f"{r+1}.0", f"{r+1}.end")
        self.ta.delete(f"{r}.0", f"{r+1}.end")
        self.ta.insert(f"{r}.0", f"{b}\n{a}")
        self.ta.mark_set("insert", f"{r+1}.{idx.split('.')[1]}")

    def _del_line(self):
        idx = self.ta.index("insert")
        r   = int(idx.split(".")[0])
        self.ta.delete(f"{r}.0", f"{r+1}.0")

    def _case(self, mode):
        try:
            sel = self.ta.get("sel.first", "sel.last")
            fn  = {"upper": str.upper, "lower": str.lower, "title": str.title}[mode]
            self.ta.delete("sel.first", "sel.last")
            self.ta.insert("insert", fn(sel))
        except tk.TclError:
            pass

    def _strip_trailing(self):
        self._push_undo()
        content = self.ta.get("1.0", "end-1c")
        cleaned = "\n".join(l.rstrip() for l in content.split("\n"))
        self._set_text(cleaned)

    def _goto_line(self):
        T = self.T
        total = int(self.ta.index("end-1c").split(".")[0])
        dlg = tk.Toplevel(self.root)
        dlg.title("Go to Line")
        dlg.geometry("280x120")
        dlg.resizable(False, False)
        dlg.configure(bg=T["panel"])
        dlg.transient(self.root)
        dlg.grab_set()
        tk.Label(dlg, text=f"Line  (1 – {total})", font=self.ui_sm,
                 bg=T["panel"], fg=T["text_fg"]).pack(pady=(18, 6))
        var = tk.StringVar()
        e = StyledEntry(dlg, T, textvariable=var, font=self.mono)
        e.pack(padx=30, fill="x")
        e.focus_set()
        def go(*_):
            try:
                n = max(1, min(int(var.get()), total))
                self.ta.mark_set("insert", f"{n}.0")
                self.ta.see(f"{n}.0")
                dlg.destroy()
            except ValueError: pass
        e.bind("<Return>", go)
        PillButton(dlg, "Go", go, T, accent=True).pack(pady=10)

    # ── FILTER ─────────────────────────────────────────────────
    def _apply_filter(self):
        q = self._fv.get().strip()
        if not q: return
        self._push_undo()
        lines = self.ta.get("1.0", "end-1c").splitlines()
        self._set_text("\n".join(l for l in lines if q.lower() in l.lower()))

    def _apply_neg_filter(self):
        q = self._nfv.get().strip()
        if not q: return
        self._push_undo()
        lines = self.ta.get("1.0", "end-1c").splitlines()
        self._set_text("\n".join(l for l in lines if q.lower() not in l.lower()))

    def _reset_filter(self):
        tab = self._cur_tab()
        if not tab: return
        self._push_undo()
        self._set_text(tab.original)

    # ── SEARCH ─────────────────────────────────────────────────
    def _live_search(self):
        self._clear_matches()
        q = self._sv.get()
        if not q: self._match_lbl.config(text=""); return
        self._run_search(q)

    def _run_search(self, q):
        flags = 0 if self._case_var.get() else re.IGNORECASE
        content = self.ta.get("1.0", "end-1c")
        try:
            if self._regex_var.get():
                pat = q
            elif self._whole_var.get():
                pat = rf"\b{re.escape(q)}\b"
            else:
                pat = re.escape(q)
            self._matches = []
            for m in re.finditer(pat, content, flags):
                s = self._offset_idx(content, m.start())
                e = self._offset_idx(content, m.end())
                self._matches.append((s, e))
                self.ta.tag_add("match", s, e)
        except re.error:
            pass
        n = len(self._matches)
        if n == 0:
            self._match_lbl.config(text="No results", fg=self.T["danger"])
        else:
            self._match_lbl.config(text=f"{n} result{'s' if n!=1 else ''}", fg=self.T["warning"])

    def _next_match(self):
        if not self._matches: self._live_search(); return
        self._match_i = (self._match_i + 1) % len(self._matches)
        self._jump()

    def _prev_match(self):
        if not self._matches: return
        self._match_i = (self._match_i - 1) % len(self._matches)
        self._jump()

    def _jump(self):
        self.ta.tag_remove("cur_match", "1.0", "end")
        if 0 <= self._match_i < len(self._matches):
            s, e = self._matches[self._match_i]
            self.ta.tag_add("cur_match", s, e)
            self.ta.see(s)
            n = len(self._matches)
            self._match_lbl.config(text=f"{self._match_i+1} / {n}", fg=self.T["warning"])

    def _clear_matches(self):
        self.ta.tag_remove("match", "1.0", "end")
        self.ta.tag_remove("cur_match", "1.0", "end")
        self._matches = []; self._match_i = -1

    def _replace_one(self):
        if not self._matches or self._match_i < 0: return
        s, e = self._matches[self._match_i]
        self.ta.delete(s, e)
        self.ta.insert(s, self._rv.get())
        self._live_search()

    def _replace_all(self):
        q = self._sv.get()
        if not q: return
        self._push_undo()
        content = self.ta.get("1.0", "end-1c")
        flags   = 0 if self._case_var.get() else re.IGNORECASE
        try:
            pat = q if self._regex_var.get() else re.escape(q)
            new, n = re.subn(pat, self._rv.get(), content, flags=flags)
        except re.error: return
        self._set_text(new)
        messagebox.showinfo("Replace All", f"Replaced {n} occurrence(s).")
        self._live_search()

    # ── PANELS ─────────────────────────────────────────────────
    def _toggle_filter(self):
        if self._filter_visible:
            self.filter_bar.pack_forget(); self._filter_visible = False
        else:
            if self._search_visible:
                self.search_bar.pack_forget(); self._search_visible = False
            self.filter_bar.pack(fill="x", side="top", after=self.tabs_outer)
            self._filter_visible = True

    def _toggle_search(self):
        if self._search_visible:
            self.search_bar.pack_forget(); self._search_visible = False
        else:
            if self._filter_visible:
                self.filter_bar.pack_forget(); self._filter_visible = False
            self.search_bar.pack(fill="x", side="top", after=self.tabs_outer)
            self._search_visible = True
            self._se.focus_set()

    def _close_panels(self):
        if self._filter_visible: self._toggle_filter()
        if self._search_visible: self._toggle_search()

    # ── WRAP / ZOOM ────────────────────────────────────────────
    def _toggle_wrap(self):
        self.ta.configure(wrap=tk.WORD if self._wrap_var.get() else tk.NONE)

    def _zoom(self, d):
        self.font_size = max(8, min(36, self.font_size + d))
        self.mono.configure(size=self.font_size)
        self.gutter.configure(font=self.mono)
        self._update_gutter()

    def _zoom_reset(self):
        self.font_size = 13
        self.mono.configure(size=self.font_size)
        self.gutter.configure(font=self.mono)

    # ── RECENT ─────────────────────────────────────────────────
    def _load_recent(self):
        try:
            with open(self.RECENT_FILE) as f:
                return json.load(f)
        except: return []

    def _add_recent(self, path):
        self._recent = [p for p in self._recent if p != path][:9]
        self._recent.insert(0, path)
        try:
            with open(self.RECENT_FILE, "w") as f:
                json.dump(self._recent, f)
        except: pass

    # ── UTIL ───────────────────────────────────────────────────
    def _set_text(self, content):
        self.ta.delete("1.0", "end")
        self.ta.insert("end", content)
        self._deferred_update()

    def _quit(self):
        dirty = [t for t in self.tabs if not t.saved]
        if dirty and not messagebox.askyesno("Quit", f"{len(dirty)} unsaved tab(s). Quit anyway?"):
            return
        self.root.destroy()


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    Nedit(sys.argv[1] if len(sys.argv) > 1 else None)
