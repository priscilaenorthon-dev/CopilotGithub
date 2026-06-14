"""
TBH Task Bar Hero — Bot de Automação
Execute via INICIAR.bat
"""

import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

MISSING_DEPS = []
try:
    import cv2
    import numpy as np
    import mss
    import pyautogui
    from PIL import Image, ImageTk
except ImportError as e:
    MISSING_DEPS.append(str(e))

# ─── Tema ───────────────────────────────────────────────────────────────────
BG     = "#1a1b2e"
BG2    = "#252640"
BG3    = "#2e2f4a"
BG4    = "#383960"
ACC    = "#7c6af7"
BLUE   = "#8be9fd"
GREEN  = "#50fa7b"
RED    = "#ff5555"
ORANGE = "#ffb86c"
YELLOW = "#f1fa8c"
WHITE  = "#f8f8f2"
GRAY   = "#6272a4"
DGREEN = "#2d5a27"

FN    = ("Segoe UI", 10)
FNB   = ("Segoe UI", 10, "bold")
FNH   = ("Segoe UI", 12, "bold")
FNS   = ("Segoe UI", 9)
MONO  = ("Consolas", 9)

COOLDOWN_MIN = 12
DEFAULT_ROUTE = ["1-9", "2-8", "3-8"]

CHEST_ROUTES = {
    "Iniciante   1-7 / 1-8 / 1-9":       ["1-7", "1-8", "1-9"],
    "Intermediário   1-9 / 2-7 / 2-8":   ["1-9", "2-7", "2-8"],
    "Avançado   1-9 / 2-8 / 3-8":        ["1-9", "2-8", "3-8"],
    "Expert   1-9 / 2-8 / 3-8 / 3-9":   ["1-9", "2-8", "3-8", "3-9"],
}

FARM_PRESETS = {
    "Exp Rápido":      ["1-7", "1-8", "1-9"],
    "Farm de Gold":    ["2-4", "2-5"],
    "Pets Morcegos":   ["1-7", "1-8", "1-9"],
    "Pets Watchers":   ["2-4", "2-5"],
    "Pets Skeletons":  ["2-8", "2-9"],
    "Pets Golems":     ["3-6"],
    "Pets Ghosts":     ["3-4", "3-5"],
    "Clear Completo":  ["1-1","1-7","1-8","2-4","3-6"],
}

STAGE_IDS = [f"{a}-{s}" for a in range(1, 4) for s in range(1, 10)]

# Templates que precisam captura manual
MANUAL_TEMPLATES = [
    ("portal_icon",  "ui",          "Aba Portal  (painel HERO)",
     "Botão 'Portal' na parte INFERIOR do painel HERO — é a 3ª aba (após Inventário e Formas)"),
    ("act1_header",  "portal_menu", "Aba Act 1  (painel PORTAL)",
     "Botão/texto 'Act 1' no TOPO do painel PORTAL — abra o Portal primeiro, depois capture"),
    ("act2_header",  "portal_menu", "Aba Act 2  (painel PORTAL)",
     "Botão/texto 'Act 2' no topo do painel PORTAL (visível ao lado de Act 1 e Act 3)"),
    ("act3_header",  "portal_menu", "Aba Act 3  (painel PORTAL)",
     "Botão/texto 'Act 3' no topo do painel PORTAL"),
]

# Templates baixados automaticamente do CDN
AUTO_TEMPLATES = [
    ("blue_chest_icon",  "ui",    "Baú Azul"),
    ("chest_act_boss",   "ui",    "Baú Act Boss"),
    ("soulstone_normal", "ui",    "Soulstone"),
    ("gold_icon",        "ui",    "Gold Icon"),
]


# ─── Helpers ────────────────────────────────────────────────────────────────

def tpl_path(name: str, sub: str) -> Path:
    return ROOT / "templates" / sub / f"{name}.png"

def tpl_exists(name: str, sub: str) -> bool:
    return tpl_path(name, sub).exists()

def log_ts() -> str:
    return datetime.now().strftime("%H:%M:%S")

def detect_game() -> bool:
    """Detecta se o TBH está rodando procurando pelos painéis HERO, PORTAL ou STASH."""
    try:
        import win32gui
        found = []
        fragments = {"HERO", "PORTAL", "STASH", "TASK BAR HERO", "TBH"}
        def _cb(hwnd, lst):
            if win32gui.IsWindowVisible(hwnd):
                t = win32gui.GetWindowText(hwnd).upper()
                if any(f in t for f in fragments):
                    lst.append(hwnd)
            return True
        win32gui.EnumWindows(_cb, found)
        return bool(found)
    except Exception:
        return False

def take_screenshot():
    with mss.mss() as sct:
        raw = sct.grab(sct.monitors[1])
        return np.array(raw)[:, :, :3]


# ─── Overlay de captura ──────────────────────────────────────────────────────

class CaptureOverlay(tk.Toplevel):
    def __init__(self, screenshot, hint: str = ""):
        super().__init__()
        self.result = None
        self._start = None
        self._rid = None
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.config(bg="black", cursor="crosshair")
        self.overrideredirect(True)

        h, w = screenshot.shape[:2]
        photo = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)))
        self._photo = photo

        self.canvas = tk.Canvas(self, width=w, height=h, highlightthickness=0, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=photo)

        tk.Label(
            self,
            text=f"🎯  {hint}\n"
                 "Clique e arraste  •  ESC para cancelar",
            bg="#16213e", fg=WHITE,
            font=("Segoe UI", 13, "bold"),
            padx=20, pady=10,
        ).place(relx=0.5, y=10, anchor="n")

        self.canvas.bind("<ButtonPress-1>", lambda e: setattr(self, '_start', (e.x, e.y)))
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.bind("<Escape>", lambda _: self.destroy())

    def _drag(self, e):
        if self._start:
            if self._rid:
                self.canvas.delete(self._rid)
            self._rid = self.canvas.create_rectangle(
                *self._start, e.x, e.y, outline=GREEN, width=2, dash=(5, 3))

    def _release(self, e):
        if self._start:
            x1, y1 = self._start
            self.result = (min(x1, e.x), min(y1, e.y), abs(e.x - x1), abs(e.y - y1))
            self.destroy()


# ═══════════════════════════════════════════════════════════════════════════
class TBHBot(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("TBH: Task Bar Hero — Automação")
        self.configure(bg=BG)
        self.minsize(720, 680)
        self.resizable(True, True)

        self._nav        = None
        self._tracker    = None
        self._stop_ev    = threading.Event()
        self._hunt_ev    = threading.Event()
        self._stage_vars : dict[str, tk.BooleanVar] = {}
        self._tpl_vars   : dict[str, tk.StringVar]  = {}
        self._hunt_route : list[str] = list(DEFAULT_ROUTE)
        self._trk_rows   : dict[str, dict] = {}
        self._setup_done = False

        for sub in ("ui", "portal_menu", "stages", "items", "heroes"):
            (ROOT / "templates" / sub).mkdir(parents=True, exist_ok=True)

        self._build()
        # Auto-inicialização em background
        threading.Thread(target=self._auto_init, daemon=True).start()

    # ────────────────────────────────────────────────────────────────────────
    # BUILD
    # ────────────────────────────────────────────────────────────────────────

    def _build(self):
        # Barra de rolagem principal
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        vs = ttk.Scrollbar(outer, orient="vertical")
        vs.pack(side="right", fill="y")

        self._cv = tk.Canvas(outer, bg=BG, highlightthickness=0, yscrollcommand=vs.set)
        self._cv.pack(side="left", fill="both", expand=True)
        vs.config(command=self._cv.yview)

        self._body = tk.Frame(self._cv, bg=BG)
        self._win  = self._cv.create_window((0, 0), window=self._body, anchor="nw")

        self._body.bind("<Configure>", lambda e: self._cv.config(
            scrollregion=self._cv.bbox("all")))
        self._cv.bind("<Configure>", lambda e: self._cv.itemconfig(self._win, width=e.width))
        self._cv.bind_all("<MouseWheel>",
            lambda e: self._cv.yview_scroll(int(-e.delta / 120), "units"))

        self._mk_header()
        self._mk_setup()
        self._mk_farm()
        self._mk_tracker()
        self._mk_log()

    # ── Cabeçalho ────────────────────────────────────────────────────────────

    def _mk_header(self):
        tk.Frame(self._body, bg=ACC, height=3).pack(fill="x")

        row = tk.Frame(self._body, bg=BG, pady=10)
        row.pack(fill="x", padx=16)

        tk.Label(row, text="🎮  TBH Task Bar Hero",
                 font=("Segoe UI", 15, "bold"), bg=BG, fg=WHITE).pack(side="left")

        right = tk.Frame(row, bg=BG)
        right.pack(side="right")

        self._gdot  = tk.Label(right, text="●", font=FNB, bg=BG, fg=RED)
        self._gdot.pack(side="left")
        self._glbl  = tk.Label(right, text=" Verificando jogo...", font=FNS, bg=BG, fg=GRAY)
        self._glbl.pack(side="left")

        tk.Frame(self._body, bg=BG3, height=1).pack(fill="x")

    # ── Setup inteligente ────────────────────────────────────────────────────

    def _mk_setup(self):
        self._setup_frm = tk.Frame(self._body, bg=BG, padx=16, pady=10)
        self._setup_frm.pack(fill="x")

        # Cabeçalho
        h = tk.Frame(self._setup_frm, bg=BG)
        h.pack(fill="x", pady=(0, 8))
        tk.Label(h, text="⚙️  CONFIGURAÇÃO",
                 font=("Segoe UI", 13, "bold"), bg=BG, fg=ACC).pack(side="left")
        self._setup_sum = tk.Label(h, text="Verificando...", font=FNS, bg=BG, fg=GRAY)
        self._setup_sum.pack(side="right")

        # Bloco de status geral
        status_box = tk.Frame(self._setup_frm, bg=BG2, padx=14, pady=10)
        status_box.pack(fill="x", pady=(0, 10))

        # Linha 1: Assets do jogo
        r1 = tk.Frame(status_box, bg=BG2)
        r1.pack(fill="x", pady=2)
        tk.Label(r1, text="Assets do jogo:", font=FNB, bg=BG2, fg=WHITE, width=22, anchor="w").pack(side="left")
        self._asset_lbl = tk.Label(r1, text="Verificando...", font=FNS, bg=BG2, fg=GRAY)
        self._asset_lbl.pack(side="left")
        self._dl_btn = tk.Button(r1, text="⬇ Baixar", font=FNS,
                                  bg=BLUE, fg=BG, relief="flat", padx=8, cursor="hand2",
                                  command=self._download_assets)
        self._dl_btn.pack(side="right")

        # Linha 2: Templates manuais
        r2 = tk.Frame(status_box, bg=BG2)
        r2.pack(fill="x", pady=2)
        tk.Label(r2, text="Templates da UI:", font=FNB, bg=BG2, fg=WHITE, width=22, anchor="w").pack(side="left")
        self._uitpl_lbl = tk.Label(r2, text="—", font=FNS, bg=BG2, fg=GRAY)
        self._uitpl_lbl.pack(side="left")

        # Linha 3: Templates de estágios
        r3 = tk.Frame(status_box, bg=BG2)
        r3.pack(fill="x", pady=2)
        tk.Label(r3, text="Templates de estágios:", font=FNB, bg=BG2, fg=WHITE, width=22, anchor="w").pack(side="left")
        self._stgtpl_lbl = tk.Label(r3, text="—", font=FNS, bg=BG2, fg=GRAY)
        self._stgtpl_lbl.pack(side="left")

        # Dica sobre o dropdown de dificuldade do PORTAL
        tip = tk.Frame(self._setup_frm, bg=BG3, padx=12, pady=6)
        tip.pack(fill="x", pady=(0, 6))
        tk.Label(tip,
                 text="💡  Antes de iniciar: no painel PORTAL do jogo, selecione a dificuldade "
                      "'Normal' no menu suspenso do topo. O bot não altera a dificuldade.",
                 font=FNS, bg=BG3, fg=YELLOW, wraplength=580, justify="left").pack(anchor="w")

        # Aviso de setup se necessário
        self._setup_warn = tk.Frame(self._setup_frm, bg=BG2, padx=12, pady=8)
        self._setup_warn_lbl = tk.Label(self._setup_warn, text="",
                                         font=FNS, bg=BG2, fg=ORANGE, wraplength=550, justify="left")
        self._setup_warn_lbl.pack(anchor="w")

        # Seção expandível de captura manual
        expand_row = tk.Frame(self._setup_frm, bg=BG)
        expand_row.pack(fill="x", pady=(6, 0))

        self._expand_var = tk.BooleanVar(value=False)
        self._expand_btn = tk.Button(
            expand_row,
            text="▶  Mostrar captura de templates manuais",
            font=FNS, bg=BG3, fg=WHITE,
            activebackground=ACC, activeforeground=WHITE,
            relief="flat", padx=10, pady=6, cursor="hand2", anchor="w",
            command=self._toggle_capture_panel,
        )
        self._expand_btn.pack(fill="x")

        self._capture_panel = tk.Frame(self._setup_frm, bg=BG)
        self._build_capture_panel()

        tk.Frame(self._body, bg=BG3, height=1).pack(fill="x")

    def _build_capture_panel(self):
        f = self._capture_panel

        # Templates obrigatórios da UI
        tk.Label(f, text="Elementos obrigatórios (capturar uma vez):",
                 font=FNB, bg=BG, fg=WHITE).pack(anchor="w", pady=(10, 4))

        for name, sub, label, hint in MANUAL_TEMPLATES:
            self._build_capture_row(f, name, sub, label, hint)

        # Separador
        tk.Frame(f, bg=BG3, height=1).pack(fill="x", pady=8)

        # Templates de estágios
        sh = tk.Frame(f, bg=BG)
        sh.pack(fill="x", pady=(0, 4))
        tk.Label(sh, text="Nós de estágio no mapa (capture só os que for usar):",
                 font=FNB, bg=BG, fg=WHITE).pack(side="left")
        tk.Label(sh, text="  Abra o Portal → clique na aba do Act → capture o ponto do estágio no mapa",
                 font=FNS, bg=BG, fg=GRAY).pack(side="left")

        grid = tk.Frame(f, bg=BG)
        grid.pack(fill="x")
        for col in range(3):
            grid.columnconfigure(col, weight=1)

        for idx, sid in enumerate(STAGE_IDS):
            name = f"stage_{sid.replace('-','_')}"
            self._build_stage_tile(grid, idx // 3, idx % 3, name, sid)

    def _build_capture_row(self, parent, name, sub, label, hint):
        row = tk.Frame(parent, bg=BG2, padx=10, pady=6)
        row.pack(fill="x", pady=2)

        sv = tk.StringVar(value="❌")
        self._tpl_vars[name] = sv
        tk.Label(row, textvariable=sv, font=("Segoe UI", 12), bg=BG2, width=3).pack(side="left")

        info = tk.Frame(row, bg=BG2)
        info.pack(side="left", fill="x", expand=True, padx=6)
        tk.Label(info, text=label, font=FNB, bg=BG2, fg=WHITE, anchor="w").pack(anchor="w")
        tk.Label(info, text=hint, font=FNS, bg=BG2, fg=GRAY, anchor="w").pack(anchor="w")

        tk.Button(
            row, text="📷  Capturar", font=FNS,
            bg=ACC, fg=WHITE,
            activebackground="#9d8ef9", activeforeground=WHITE,
            relief="flat", padx=10, pady=4, cursor="hand2",
            command=lambda n=name, s=sub, l=label, h=hint: self._do_capture(n, s, l, h),
        ).pack(side="right")

    def _build_stage_tile(self, parent, row, col, name, sid):
        tile = tk.Frame(parent, bg=BG2, padx=8, pady=5)
        tile.grid(row=row, column=col, padx=3, pady=3, sticky="ew")

        sv = tk.StringVar(value="❌")
        self._tpl_vars[name] = sv

        left = tk.Frame(tile, bg=BG2)
        left.pack(side="left", fill="x", expand=True)
        top = tk.Frame(left, bg=BG2)
        top.pack(anchor="w")
        tk.Label(top, textvariable=sv, font=("Segoe UI", 10), bg=BG2).pack(side="left")
        tk.Label(top, text=f"  Estágio {sid}", font=FNB, bg=BG2, fg=WHITE).pack(side="left")

        tk.Button(
            tile, text="📷", font=("Segoe UI", 9),
            bg=BG3, fg=WHITE,
            activebackground=ACC, activeforeground=WHITE,
            relief="flat", padx=6, pady=2, cursor="hand2",
            command=lambda n=name, s=sid: self._do_capture(
                n, "stages", f"Nó do Estágio {s}",
                f"Ponto/círculo do estágio {s} no MAPA do painel PORTAL "
                f"(clique na aba Act {s[0]} primeiro para ver o mapa)"),
        ).pack(side="right")

    def _toggle_capture_panel(self):
        if self._expand_var.get():
            self._capture_panel.pack_forget()
            self._expand_btn.config(text="▶  Mostrar captura de templates manuais")
            self._expand_var.set(False)
        else:
            self._capture_panel.pack(fill="x")
            self._expand_btn.config(text="▼  Ocultar captura de templates manuais")
            self._expand_var.set(True)

    # ── Farm loop ────────────────────────────────────────────────────────────

    def _mk_farm(self):
        frm = tk.Frame(self._body, bg=BG, padx=16, pady=10)
        frm.pack(fill="x")

        tk.Label(frm, text="🗺  AUTOMAÇÃO DE MAPAS",
                 font=FNH, bg=BG, fg=ACC).pack(anchor="w", pady=(0, 8))

        body = tk.Frame(frm, bg=BG)
        body.pack(fill="x")

        # ── Esquerda: checkboxes ────────────────────────────────────────────
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(left, text="Selecione os mapas:", font=FNB, bg=BG, fg=WHITE).pack(anchor="w")

        lf = tk.Frame(left, bg=BG2)
        lf.pack(fill="both", expand=True, pady=(4, 0))

        ys = ttk.Scrollbar(lf, orient="vertical")
        self._scv = tk.Canvas(lf, bg=BG2, highlightthickness=0,
                               yscrollcommand=ys.set, width=230, height=200)
        ys.config(command=self._scv.yview)
        self._scv.pack(side="left", fill="both", expand=True)
        ys.pack(side="right", fill="y")

        self._sci = tk.Frame(self._scv, bg=BG2)
        self._scv.create_window((0, 0), window=self._sci, anchor="nw")
        self._sci.bind("<Configure>", lambda e: self._scv.config(
            scrollregion=self._scv.bbox("all")))

        for act in range(1, 4):
            tk.Label(self._sci, text=f"  Act {act}",
                     font=FNB, bg=BG2, fg=ACC).pack(anchor="w", pady=(6, 2))
            for s in range(1, 10):
                sid = f"{act}-{s}"
                var = tk.BooleanVar(value=False)
                self._stage_vars[sid] = var
                tk.Checkbutton(
                    self._sci, text=f"  Estágio {sid}", variable=var,
                    bg=BG2, fg=WHITE, selectcolor=ACC,
                    activebackground=BG2, activeforeground=WHITE,
                    font=FNS, anchor="w",
                ).pack(fill="x", padx=8)

        sel = tk.Frame(left, bg=BG)
        sel.pack(fill="x", pady=(4, 0))
        for txt, cmd in [("Todos", self._sel_all), ("Nenhum", self._sel_none)]:
            tk.Button(sel, text=txt, font=FNS, bg=BG3, fg=WHITE,
                      relief="flat", padx=6, cursor="hand2",
                      command=cmd).pack(side="left", padx=(0, 4))

        # ── Direita: presets ────────────────────────────────────────────────
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="y", padx=(8, 0))

        tk.Label(right, text="Presets:", font=FNB, bg=BG, fg=WHITE).pack(anchor="w")

        pb = tk.Frame(right, bg=BG2, padx=8, pady=8)
        pb.pack(fill="y", expand=True, pady=(4, 0))

        for label, stages in FARM_PRESETS.items():
            tk.Button(
                pb,
                text=f"  {label}\n  ({', '.join(stages)})",
                font=FNS, bg=BG3, fg=WHITE,
                activebackground=ACC, activeforeground=WHITE,
                relief="flat", anchor="w", padx=8, pady=4, cursor="hand2",
                justify="left",
                command=lambda s=stages: self._apply_preset(s),
            ).pack(fill="x", pady=2)

        # ── Controles ───────────────────────────────────────────────────────
        tk.Frame(frm, bg=BG3, height=1).pack(fill="x", pady=10)

        ctrl = tk.Frame(frm, bg=BG)
        ctrl.pack(fill="x")

        # Repetições
        rf = tk.Frame(ctrl, bg=BG)
        rf.pack(side="left", padx=(0, 16))
        tk.Label(rf, text="Repetições:", font=FNS, bg=BG, fg=GRAY).pack(anchor="w")
        self._iter = tk.StringVar(value="∞ Infinito")
        ttk.Combobox(rf, textvariable=self._iter,
                     values=["∞ Infinito","1x","3x","5x","10x","25x","50x"],
                     state="readonly", width=12).pack()

        bf = tk.Frame(ctrl, bg=BG)
        bf.pack(side="left")

        self._farm_btn = tk.Button(
            bf, text="▶  INICIAR FARM",
            font=("Segoe UI", 11, "bold"),
            bg=GREEN, fg="#1e1e2e",
            activebackground="#3dbb5e", activeforeground="#1e1e2e",
            relief="flat", padx=18, pady=8, cursor="hand2",
            command=self._farm_start,
        )
        self._farm_btn.pack(side="left", padx=(0, 8))

        self._once_btn = tk.Button(
            bf, text="→  Ir uma vez",
            font=FN, bg=BG3, fg=WHITE,
            activebackground=ACC, activeforeground=WHITE,
            relief="flat", padx=12, pady=8, cursor="hand2",
            command=self._navigate_once,
        )
        self._once_btn.pack(side="left", padx=(0, 8))

        self._farm_stop = tk.Button(
            bf, text="■  Parar",
            font=("Segoe UI", 11, "bold"),
            bg=RED, fg=WHITE,
            activebackground="#cc4444", activeforeground=WHITE,
            relief="flat", padx=14, pady=8, cursor="hand2",
            state="disabled",
            command=self._farm_stop_fn,
        )
        self._farm_stop.pack(side="left")

        self._farm_status = tk.Label(ctrl, text="", font=FNS, bg=BG, fg=YELLOW)
        self._farm_status.pack(side="right")

        tk.Frame(self._body, bg=BG3, height=1).pack(fill="x")

    # ── Tracker de baús ──────────────────────────────────────────────────────

    def _mk_tracker(self):
        frm = tk.Frame(self._body, bg=BG, padx=16, pady=10)
        frm.pack(fill="x")

        # Cabeçalho
        h = tk.Frame(frm, bg=BG)
        h.pack(fill="x", pady=(0, 6))

        tk.Label(h, text="🔵  TRACKER DE BAÚS AZUIS",
                 font=FNH, bg=BG, fg=BLUE).pack(side="left")

        self._chest_lbl = tk.Label(h, text="", font=("Segoe UI", 11, "bold"), bg=BG, fg=GREEN)
        self._chest_lbl.pack(side="right")

        # Info
        ib = tk.Frame(frm, bg=BG2, padx=12, pady=8)
        ib.pack(fill="x", pady=(0, 10))
        tk.Label(ib,
                 text="⏱  Cada estágio tem 12 min de cooldown independente  •  "
                      "Bot clica aba Portal → seleciona Act → clica nó do estágio no mapa → "
                      "aguarda combate → detecta baú e clica automaticamente",
                 font=FNS, bg=BG2, fg=WHITE, wraplength=620, justify="left").pack(anchor="w")

        # Seleção de rota
        rf = tk.Frame(frm, bg=BG)
        rf.pack(fill="x", pady=(0, 10))

        tk.Label(rf, text="Rota:", font=FNB, bg=BG, fg=WHITE).pack(side="left")
        self._route_var = tk.StringVar(value="Avançado   1-9 / 2-8 / 3-8")
        route_cb = ttk.Combobox(rf, textvariable=self._route_var,
                                 values=list(CHEST_ROUTES.keys()),
                                 state="readonly", width=38)
        route_cb.pack(side="left", padx=8)
        route_cb.bind("<<ComboboxSelected>>", self._route_changed)

        self._route_lbl = tk.Label(rf, text="→ 1-9, 2-8, 3-8",
                                    font=FNS, bg=BG, fg=GRAY)
        self._route_lbl.pack(side="left")

        # Tabela
        tbl = tk.Frame(frm, bg=BG2)
        tbl.pack(fill="x", pady=(0, 10))

        thead = tk.Frame(tbl, bg=BG3)
        thead.pack(fill="x")
        for txt, w in [("Estágio", 10), ("Último Farm", 14), ("Próximo em", 10), ("", 1), ("Status", 24)]:
            tk.Label(thead, text=txt, font=FNB, bg=BG3, fg=GRAY,
                     width=w, anchor="w").pack(side="left", padx=6, pady=4)

        self._tbl_body = tk.Frame(tbl, bg=BG2)
        self._tbl_body.pack(fill="x")
        self._rebuild_table()

        # Stats
        sb = tk.Frame(frm, bg=BG3, padx=12, pady=6)
        sb.pack(fill="x", pady=(0, 10))

        self._sv_total  = tk.StringVar(value="🔵 Baús: 0")
        self._sv_best   = tk.StringVar(value="Melhor: —")
        self._sv_uptime = tk.StringVar(value="Sessão: —")
        self._sv_last   = tk.StringVar(value="Último: —")

        for sv in (self._sv_total, self._sv_best, self._sv_uptime, self._sv_last):
            tk.Label(sb, textvariable=sv, font=FNS, bg=BG3, fg=WHITE).pack(side="left", padx=14)

        # Botões
        bc = tk.Frame(frm, bg=BG)
        bc.pack(fill="x")

        self._hunt_btn = tk.Button(
            bc, text="🔵  CAÇAR BAÚS AUTO",
            font=("Segoe UI", 12, "bold"),
            bg=BLUE, fg=BG,
            activebackground="#6acfe8", activeforeground=BG,
            relief="flat", padx=20, pady=10, cursor="hand2",
            command=self._hunt_start,
        )
        self._hunt_btn.pack(side="left", padx=(0, 12))

        self._hunt_stop = tk.Button(
            bc, text="■  Parar",
            font=("Segoe UI", 11, "bold"),
            bg=RED, fg=WHITE,
            activebackground="#cc4444", activeforeground=WHITE,
            relief="flat", padx=14, pady=10, cursor="hand2",
            state="disabled",
            command=self._hunt_stop_fn,
        )
        self._hunt_stop.pack(side="left")

        # Cooldown manual
        mc = tk.Frame(bc, bg=BG)
        mc.pack(side="right")
        tk.Label(mc, text="Cooldown (min):", font=FNS, bg=BG, fg=GRAY).pack(side="left")
        self._cd_var = tk.IntVar(value=COOLDOWN_MIN)
        ttk.Spinbox(mc, from_=5, to=30, textvariable=self._cd_var,
                    width=5, command=self._cd_changed).pack(side="left", padx=4)

        self._hunt_st = tk.Label(bc, text="", font=FNS, bg=BG, fg=YELLOW)
        # won't pack yet

        tk.Frame(self._body, bg=BG3, height=1).pack(fill="x")

        # Clock tick
        threading.Thread(target=self._clock_loop, daemon=True).start()

    def _rebuild_table(self):
        for w in self._tbl_body.winfo_children():
            w.destroy()
        self._trk_rows = {}

        for sid in self._hunt_route:
            row = tk.Frame(self._tbl_body, bg=BG2)
            row.pack(fill="x")

            tk.Label(row, text=f"  {sid}", font=FNB, bg=BG2, fg=WHITE,
                     width=10, anchor="w").pack(side="left", pady=4)

            last_l = tk.Label(row, text="—", font=FNS, bg=BG2, fg=GRAY, width=14, anchor="w")
            last_l.pack(side="left", padx=4)

            cd_l = tk.Label(row, text="PRONTO!", font=FNB, bg=BG2, fg=GREEN, width=10, anchor="w")
            cd_l.pack(side="left", padx=4)

            # Barra de progresso
            bar_f = tk.Frame(row, bg=BG3, width=150, height=14)
            bar_f.pack_propagate(False)
            bar_fill = tk.Frame(bar_f, bg=GREEN, height=14)
            bar_fill.place(x=0, y=0, relwidth=1.0, height=14)
            bar_f.pack(side="left", padx=8)

            st_l = tk.Label(row, text="✅ PRONTO!", font=FNB, bg=BG2, fg=GREEN, anchor="w")
            st_l.pack(side="left", padx=4)

            tk.Frame(self._tbl_body, bg=BG3, height=1).pack(fill="x")

            self._trk_rows[sid] = {"last": last_l, "cd": cd_l, "fill": bar_fill, "st": st_l}

    def _clock_loop(self):
        while True:
            self.after(0, self._tick)
            time.sleep(1)

    def _tick(self):
        tr = self._get_tracker()
        for sid in self._hunt_route:
            t = tr.get_stage(sid)
            row = self._trk_rows.get(sid)
            if not row:
                continue
            row["last"].config(text=t.last_collected_str)
            row["cd"].config(text=t.countdown_str)

            p = t.progress
            color = GREEN if p >= 1.0 else (YELLOW if p >= 0.66 else (ORANGE if p >= 0.33 else RED))
            row["fill"].place(relwidth=min(p, 1.0))
            row["fill"].config(bg=color)
            st = "✅ PRONTO!" if t.is_ready else f"⏳ {t.countdown_str}"
            row["st"].config(text=st, fg=color)
            row["cd"].config(fg=color)

        st = tr.session
        self._sv_total.set(f"🔵 Baús: {st.total_chests}")
        self._sv_best.set(f"Melhor: {st.best_stage or '—'}")
        self._sv_uptime.set(f"Sessão: {st.uptime_str}")

    # ── AUTO INIT ────────────────────────────────────────────────────────────

    def _auto_init(self):
        """Runs on startup: check game, download assets, report status."""
        self._log("🚀 Iniciando verificação automática...", "dim")

        # 1. Detectar jogo
        game_ok = detect_game()
        self.after(0, lambda: self._update_game_status(game_ok))

        # 2. Verificar assets do CDN
        self.after(0, lambda: self._asset_lbl.config(text="Verificando assets...", fg=GRAY))
        total_auto = len(AUTO_TEMPLATES)
        present_auto = sum(1 for n, s, _ in AUTO_TEMPLATES if tpl_exists(n, s))

        if present_auto < total_auto:
            self._log(f"⬇ Baixando {total_auto - present_auto} assets do jogo...", "info")
            self.after(0, lambda: self._asset_lbl.config(
                text="Baixando...", fg=YELLOW))
            self._run_download(silent=True)
        else:
            self.after(0, lambda: self._asset_lbl.config(
                text=f"✅ {present_auto}/{total_auto} prontos", fg=GREEN))

        # 3. Verificar templates manuais
        self.after(500, self._check_all_status)

    def _run_download(self, silent=False):
        script = ROOT / "scripts" / "download_assets.py"
        try:
            result = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, timeout=60
            )
            if not silent:
                for line in result.stdout.splitlines():
                    tag = "ok" if "✅" in line else ("err" if "❌" in line else "dim")
                    if line.strip():
                        self._log(line.strip(), tag)
            self.after(0, self._check_all_status)
        except Exception as e:
            self._log(f"Erro no download: {e}", "err")

    def _check_all_status(self):
        # Assets automáticos
        total_auto = len(AUTO_TEMPLATES)
        present_auto = sum(1 for n, s, _ in AUTO_TEMPLATES if tpl_exists(n, s))
        if present_auto == total_auto:
            self._asset_lbl.config(text=f"✅ {present_auto}/{total_auto} prontos", fg=GREEN)
        else:
            self._asset_lbl.config(
                text=f"⚠ {present_auto}/{total_auto} — clique Baixar", fg=ORANGE)

        # Templates manuais
        manual_ok = sum(1 for n, s, _, _ in MANUAL_TEMPLATES if tpl_exists(n, s))
        total_man = len(MANUAL_TEMPLATES)
        if manual_ok == total_man:
            self._uitpl_lbl.config(text=f"✅ {manual_ok}/{total_man} capturados", fg=GREEN)
        else:
            self._uitpl_lbl.config(
                text=f"⚠ {manual_ok}/{total_man} — abra o painel de captura abaixo",
                fg=ORANGE)

        # Templates de estágios
        stage_ok = sum(1 for sid in STAGE_IDS
                       if tpl_exists(f"stage_{sid.replace('-','_')}", "stages"))
        total_stg = len(STAGE_IDS)
        if stage_ok == 0:
            self._stgtpl_lbl.config(text="⚠ Nenhum — capture os estágios que for usar", fg=ORANGE)
        else:
            self._stgtpl_lbl.config(
                text=f"✅ {stage_ok}/{total_stg} — capture mais conforme precisar", fg=GREEN)

        # Status geral e sugestões
        missing = []
        for name, sub, label, _ in MANUAL_TEMPLATES:
            if not tpl_exists(name, sub):
                missing.append(f"• {label}")

        if missing:
            self._setup_warn_lbl.config(
                text="⚠  Captura necessária (expanda o painel abaixo):\n" + "\n".join(missing))
            self._setup_warn.pack(fill="x", pady=(0, 6))
            # Auto-expandir painel se há templates faltando
            if not self._expand_var.get():
                self._toggle_capture_panel()
        else:
            self._setup_warn.pack_forget()
            self._setup_sum.config(text="✅ Sistema pronto!", fg=GREEN)
            if self._expand_var.get():
                self._toggle_capture_panel()

        # Atualizar vars de ícone por template
        for name, sub, label, _ in MANUAL_TEMPLATES:
            if name in self._tpl_vars:
                self._tpl_vars[name].set("✅" if tpl_exists(name, sub) else "❌")

        for sid in STAGE_IDS:
            name = f"stage_{sid.replace('-','_')}"
            if name in self._tpl_vars:
                self._tpl_vars[name].set("✅" if tpl_exists(name, "stages") else "❌")

        ok_total = manual_ok
        self._setup_sum.config(
            text=f"UI: {manual_ok}/{total_man}  •  Estágios: {stage_ok}",
            fg=GREEN if manual_ok == total_man else ORANGE,
        )

    # ── Game monitor ─────────────────────────────────────────────────────────

    def _start_game_monitor(self):
        def _loop():
            while True:
                ok = detect_game()
                self.after(0, lambda v=ok: self._update_game_status(v))
                time.sleep(5)
        threading.Thread(target=_loop, daemon=True).start()

    def _update_game_status(self, ok: bool):
        self._gdot.config(fg=GREEN if ok else RED)
        self._glbl.config(
            text=" Jogo detectado ✓" if ok else " Jogo não detectado",
            fg=GREEN if ok else RED,
        )

    # ── Captura de templates ──────────────────────────────────────────────────

    def _do_capture(self, name, sub, label, hint):
        self._log(f"Preparando captura: {label}...", "info")
        self.after(200, lambda: self._capture_flow(name, sub, label, hint))

    def _capture_flow(self, name, sub, label, hint):
        self.iconify()
        time.sleep(0.5)
        try:
            ss = take_screenshot()
        except Exception as e:
            self.deiconify()
            self._log(f"Erro ao capturar tela: {e}", "err")
            return
        self.deiconify()

        ov = CaptureOverlay(ss, hint=label)
        self.wait_window(ov)

        if not ov.result:
            self._log("Captura cancelada.", "warn")
            return

        x, y, w, h = ov.result
        if w < 4 or h < 4:
            self._log("Região muito pequena — tente novamente.", "warn")
            return

        crop = ss[y:y+h, x:x+w]
        p = tpl_path(name, sub)
        p.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(p), crop)

        self._log(f"✅ '{label}' salvo em templates/{sub}/{name}.png", "ok")
        self.after(0, self._check_all_status)

    def _download_assets(self):
        self._log("⬇ Baixando assets do jogo...", "info")
        self._asset_lbl.config(text="Baixando...", fg=YELLOW)
        self._dl_btn.config(state="disabled")
        threading.Thread(target=lambda: (
            self._run_download(silent=False),
            self.after(0, lambda: self._dl_btn.config(state="normal"))
        ), daemon=True).start()

    # ── Farm ─────────────────────────────────────────────────────────────────

    def _get_nav(self):
        if self._nav is None:
            from tbh.config import Config
            from tbh import build_navigator
            cfg = Config.load(base_dir=ROOT)
            self._nav = build_navigator(cfg)
            self._nav.set_status_callback(lambda m: self._log(m, "info"))
        return self._nav

    def _get_tracker(self):
        if self._tracker is None:
            from tbh.tracker import ChestTracker
            self._tracker = ChestTracker(cooldown_minutes=self._cd_var.get())
        return self._tracker

    def _check_ui_ready(self):
        missing = [label for name, sub, label, _ in MANUAL_TEMPLATES
                   if not tpl_exists(name, sub)]
        if missing:
            return "Templates obrigatórios faltando:\n• " + "\n• ".join(missing)
        return None

    def _get_selected(self):
        return [sid for sid, var in self._stage_vars.items() if var.get()]

    def _get_iters(self):
        v = self._iter.get()
        if "∞" in v:
            return None
        try:
            return int(v.replace("x", ""))
        except ValueError:
            return None

    def _farm_start(self):
        stages = self._get_selected()
        if not stages:
            messagebox.showwarning("Nenhum mapa", "Selecione pelo menos um estágio.")
            return

        err = self._check_ui_ready()
        if err:
            messagebox.showerror("Falta configuração", err)
            return

        missing_s = [s for s in stages
                     if not tpl_exists(f"stage_{s.replace('-','_')}", "stages")]
        if missing_s:
            messagebox.showerror("Templates faltando",
                                  "Capture os templates:\n• " + "\n• ".join(missing_s))
            return

        iters = self._get_iters()
        self._log(f"▶ Farm: {stages}  ({'∞' if iters is None else f'{iters}x'})", "ok")
        self._set_farm_running(True)
        self._stop_ev.clear()
        threading.Thread(
            target=self._farm_thread, args=(stages, iters), daemon=True
        ).start()

    def _farm_thread(self, stages, iters):
        try:
            self._get_nav().farm_loop(stages, iterations=iters, stop_event=self._stop_ev)
        except Exception as e:
            self._log(f"Erro: {e}", "err")
        finally:
            self.after(0, lambda: self._set_farm_running(False))

    def _navigate_once(self):
        stages = self._get_selected()
        if len(stages) != 1:
            messagebox.showwarning("Seleção", "Selecione exatamente 1 estágio.")
            return
        err = self._check_ui_ready()
        if err:
            messagebox.showerror("Falta configuração", err)
            return
        missing_s = [s for s in stages
                     if not tpl_exists(f"stage_{s.replace('-','_')}", "stages")]
        if missing_s:
            messagebox.showerror("Template faltando",
                                  f"Capture o template do estágio {missing_s[0]} primeiro.")
            return
        self._set_farm_running(True)
        self._stop_ev.clear()
        threading.Thread(
            target=lambda s=stages[0]: (
                self._get_nav().navigate_to(s),
                self.after(0, lambda: self._set_farm_running(False))
            ), daemon=True
        ).start()

    def _farm_stop_fn(self):
        self._stop_ev.set()
        self._log("Parando após ciclo atual...", "warn")
        self._set_farm_running(False)

    def _set_farm_running(self, v):
        s = "disabled" if v else "normal"
        self._farm_btn.config(state=s)
        self._once_btn.config(state=s)
        self._farm_stop.config(state="normal" if v else "disabled")
        self._farm_status.config(text="⏳ Rodando..." if v else "")

    # ── Chest hunt ───────────────────────────────────────────────────────────

    def _hunt_start(self):
        err = self._check_ui_ready()
        if err:
            messagebox.showerror("Falta configuração", err)
            return

        missing_s = [s for s in self._hunt_route
                     if not tpl_exists(f"stage_{s.replace('-','_')}", "stages")]
        if missing_s:
            messagebox.showerror("Templates faltando",
                                  "Capture os estágios da rota:\n• " + "\n• ".join(missing_s))
            return

        self._log(f"🔵 Caçada iniciada — rota: {self._hunt_route}", "ok")
        self._hunt_ev.clear()
        self._set_hunt_running(True)

        nav = self._get_nav()
        nav.set_chest_callback(lambda sid: self.after(0, lambda s=sid: self._chest_found(s)))

        threading.Thread(target=self._hunt_thread_fn, daemon=True).start()

    def _hunt_thread_fn(self):
        tracker = self._get_tracker()
        nav = self._get_nav()
        route = self._hunt_route

        try:
            while not self._hunt_ev.is_set():
                ready = tracker.get_ready_stages(route)

                if ready:
                    for sid in ready:
                        if self._hunt_ev.is_set():
                            break
                        try:
                            self._log(f"→ Navegando para {sid} (baú disponível)", "info")
                            nav.navigate_to(sid)
                            nav.wait_for_stage_completion()
                            nav.watch_for_chest(sid, timeout_seconds=25)
                            tracker.mark_collected(sid)
                        except Exception as e:
                            self._log(f"Erro em {sid}: {e}", "err")
                            time.sleep(3)
                else:
                    wait = max(10, min(tracker.next_ready_in(route), 30))
                    m, s = divmod(wait, 60)
                    self._log(f"⏳ Cooldown ativo. Aguardando {m:02d}:{s:02d}...", "dim")
                    for _ in range(wait):
                        if self._hunt_ev.is_set():
                            break
                        time.sleep(1)
        except Exception as e:
            self._log(f"Erro na caçada: {e}", "err")
        finally:
            self.after(0, lambda: self._set_hunt_running(False))
            self._log("Caçada encerrada.", "warn")

    def _hunt_stop_fn(self):
        self._hunt_ev.set()
        self._log("Parando caçada...", "warn")
        self._set_hunt_running(False)

    def _set_hunt_running(self, v):
        self._hunt_btn.config(state="disabled" if v else "normal")
        self._hunt_stop.config(state="normal" if v else "disabled")

    def _chest_found(self, sid: str):
        self._log(f"🔵 BAÚ AZUL coletado em {sid}!", "ok")
        self._sv_last.set(f"Último: {sid} às {log_ts()}")
        self._flash_alert(sid)

    def _flash_alert(self, sid: str):
        frames = [
            (f"🔵  BAÚ COLETADO — {sid}", GREEN),
            ("", BG),
            (f"🔵  BAÚ COLETADO — {sid}", GREEN),
            ("", BG),
            (f"🔵  BAÚ COLETADO — {sid}", WHITE),
        ]
        def _cycle(i=0):
            if i < len(frames):
                txt, col = frames[i]
                self._chest_lbl.config(text=txt, fg=col)
                self.after(350, lambda: _cycle(i + 1))
            else:
                self._chest_lbl.config(text="")
        _cycle()

    def _route_changed(self, _=None):
        name = self._route_var.get()
        self._hunt_route = list(CHEST_ROUTES.get(name, DEFAULT_ROUTE))
        self._route_lbl.config(text="→ " + ", ".join(self._hunt_route))
        self._rebuild_table()

    def _cd_changed(self):
        if self._tracker:
            self._tracker.cooldown_minutes = self._cd_var.get()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _apply_preset(self, stages):
        for sid, var in self._stage_vars.items():
            var.set(sid in stages)
        self._log(f"Preset: {stages}", "dim")

    def _sel_all(self):
        for v in self._stage_vars.values():
            v.set(True)

    def _sel_none(self):
        for v in self._stage_vars.values():
            v.set(False)

    def _log(self, msg: str, tag: str = "info"):
        def _w():
            self._log_widget.config(state="normal")
            self._log_widget.insert(tk.END, f"[{log_ts()}]  ", "dim")
            self._log_widget.insert(tk.END, msg + "\n", tag)
            self._log_widget.see(tk.END)
            self._log_widget.config(state="disabled")
            self._farm_status.config(text=msg[:52] + ("…" if len(msg) > 52 else ""))
        self.after(0, _w)

    def _clear_log(self):
        self._log_widget.config(state="normal")
        self._log_widget.delete("1.0", tk.END)
        self._log_widget.config(state="disabled")

    # ── Log ──────────────────────────────────────────────────────────────────

    def _mk_log(self):
        lf = tk.Frame(self._body, bg=BG, padx=16, pady=8)
        lf.pack(fill="both", expand=True)

        h = tk.Frame(lf, bg=BG)
        h.pack(fill="x", pady=(0, 4))
        tk.Label(h, text="📋  Log de Atividade", font=FNB, bg=BG, fg=WHITE).pack(side="left")
        tk.Button(h, text="Limpar", font=FNS, bg=BG3, fg=GRAY,
                  relief="flat", padx=6, cursor="hand2",
                  command=self._clear_log).pack(side="right")

        self._log_widget = scrolledtext.ScrolledText(
            lf, height=9, font=MONO,
            bg=BG2, fg=WHITE, insertbackground=WHITE,
            state="disabled", relief="flat", padx=8, pady=6,
        )
        self._log_widget.pack(fill="both", expand=True)

        for tag, color in [("ok",GREEN),("err",RED),("warn",ORANGE),("info",WHITE),("dim",GRAY)]:
            self._log_widget.tag_configure(tag, foreground=color)


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    if MISSING_DEPS:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Dependências faltando",
            "Instale as dependências executando INICIAR.bat:\n\n" + "\n".join(MISSING_DEPS)
        )
        root.destroy()
        sys.exit(1)

    app = TBHBot()
    app.mainloop()


if __name__ == "__main__":
    main()
