"""
TBH Task Bar Hero — Bot de Automação
Execute via INICIAR.bat
"""

import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# ── Verificação de dependências ─────────────────────────────────────────────
MISSING = []
try:
    import cv2
    import numpy as np
    import mss
    import pyautogui
    from PIL import Image, ImageTk
except ImportError as e:
    MISSING.append(str(e))

# ── Constantes de tema ──────────────────────────────────────────────────────
BG       = "#1e1e2e"
BG2      = "#2a2a3e"
BG3      = "#313145"
ACCENT   = "#7c6af7"
GREEN    = "#50fa7b"
RED      = "#ff5555"
ORANGE   = "#ffb86c"
YELLOW   = "#f1fa8c"
WHITE    = "#f8f8f2"
GRAY     = "#6272a4"
FONT     = ("Segoe UI", 10)
FONT_B   = ("Segoe UI", 10, "bold")
FONT_H   = ("Segoe UI", 13, "bold")
FONT_S   = ("Segoe UI", 9)
MONO     = ("Consolas", 9)

# ── Descrições dos templates para guiar o usuário ──────────────────────────
REQUIRED_TEMPLATES = [
    ("portal_icon",   "ui",          "Ícone do Portal",     "Ícone azul no canto INFERIOR DIREITO da janela do jogo"),
    ("act1_header",   "portal_menu", "Cabeçalho 'Act 1'",   "Label 'Act 1' dentro do menu do portal"),
    ("act2_header",   "portal_menu", "Cabeçalho 'Act 2'",   "Label 'Act 2' dentro do menu do portal"),
    ("act3_header",   "portal_menu", "Cabeçalho 'Act 3'",   "Label 'Act 3' dentro do menu do portal"),
]

STAGE_TEMPLATES = [
    ("stage_1_1", "1-1"), ("stage_1_2", "1-2"), ("stage_1_3", "1-3"),
    ("stage_1_4", "1-4"), ("stage_1_5", "1-5"), ("stage_1_6", "1-6"),
    ("stage_1_7", "1-7"), ("stage_1_8", "1-8"), ("stage_1_9", "1-9"),
    ("stage_2_1", "2-1"), ("stage_2_2", "2-2"), ("stage_2_3", "2-3"),
    ("stage_2_4", "2-4"), ("stage_2_5", "2-5"), ("stage_2_6", "2-6"),
    ("stage_2_7", "2-7"), ("stage_2_8", "2-8"), ("stage_2_9", "2-9"),
    ("stage_3_1", "3-1"), ("stage_3_2", "3-2"), ("stage_3_3", "3-3"),
    ("stage_3_4", "3-4"), ("stage_3_5", "3-5"), ("stage_3_6", "3-6"),
    ("stage_3_7", "3-7"), ("stage_3_8", "3-8"), ("stage_3_9", "3-9"),
]

FARM_PRESETS = {
    "exp_farm":       ("Exp Rápido",       ["1-7", "1-8", "1-9"]),
    "gold_farm":      ("Farm de Gold",      ["2-4", "2-5"]),
    "pet_bats":       ("Pets — Morcegos",   ["1-7", "1-8", "1-9"]),
    "pet_watchers":   ("Pets — Watchers",   ["2-4", "2-5"]),
    "pet_skeletons":  ("Pets — Skeletons",  ["2-8", "2-9"]),
    "pet_golems":     ("Pets — Golems",     ["3-6"]),
    "pet_ghosts":     ("Pets — Ghosts",     ["3-4", "3-5"]),
    "full_clear":     ("Clear Completo",    ["1-1","1-7","1-8","2-4","3-6"]),
}


# ═══════════════════════════════════════════════════════════════════════════
# OVERLAY DE CAPTURA DE REGIÃO
# ═══════════════════════════════════════════════════════════════════════════

class CaptureOverlay(tk.Toplevel):
    """Fullscreen overlay para o usuário selecionar uma região da tela."""

    def __init__(self, screenshot: "np.ndarray", hint: str = ""):
        super().__init__()
        self.screenshot = screenshot
        self.result: tuple | None = None
        self._start: tuple | None = None
        self._rect_id = None

        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.config(bg="black", cursor="crosshair")
        self.overrideredirect(True)

        h, w = screenshot.shape[:2]
        img = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
        self._photo = ImageTk.PhotoImage(img)

        self.canvas = tk.Canvas(self, width=w, height=h, highlightthickness=0, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)

        # Escurecer levemente com um overlay semi-transparente
        overlay = tk.Label(self, bg="black")
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.lower()

        # Instrução no topo
        if hint:
            hint_text = f"  CAPTURANDO: {hint}  "
        else:
            hint_text = "  Selecione a região  "

        info = tk.Label(
            self,
            text=f"🎯 {hint_text}\n"
                 "Clique e arraste ao redor do elemento  •  ESC para cancelar",
            bg="#282a36", fg=WHITE,
            font=("Segoe UI", 12, "bold"),
            padx=16, pady=8,
            relief="flat",
        )
        info.place(relx=0.5, rely=0, anchor="n", y=12)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Escape>", lambda _: self.destroy())
        self.canvas.tag_raise("all")

    def _on_press(self, e):
        self._start = (e.x, e.y)
        if self._rect_id:
            self.canvas.delete(self._rect_id)

    def _on_drag(self, e):
        if self._start:
            if self._rect_id:
                self.canvas.delete(self._rect_id)
            self._rect_id = self.canvas.create_rectangle(
                *self._start, e.x, e.y,
                outline="#50fa7b", width=2, dash=(4, 2),
            )

    def _on_release(self, e):
        if self._start:
            x1, y1 = self._start
            x2, y2 = e.x, e.y
            self.result = (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            self.destroy()


# ═══════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════

def template_path(name: str, subfolder: str) -> Path:
    return ROOT / "templates" / subfolder / f"{name}.png"

def template_exists(name: str, subfolder: str) -> bool:
    return template_path(name, subfolder).exists()

def stage_subfolder(name: str) -> str:
    if name.startswith("stage_"):
        return "stages"
    if "header" in name:
        return "portal_menu"
    return "ui"

def take_screenshot() -> "np.ndarray":
    with mss.mss() as sct:
        mon = sct.monitors[1]
        raw = sct.grab(mon)
        return np.array(raw)[:, :, :3]

def detect_game_window() -> bool:
    try:
        import win32gui
        found = []
        win32gui.EnumWindows(
            lambda h, l: l.append(h) if win32gui.IsWindowVisible(h) and
            "Task Bar Hero" in win32gui.GetWindowText(h) else None,
            found,
        )
        return len(found) > 0
    except Exception:
        return False

def log_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ═══════════════════════════════════════════════════════════════════════════
# APLICAÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

class TBHBot(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("TBH: Task Bar Hero — Bot de Automação")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._stop_event = threading.Event()
        self._farm_thread: threading.Thread | None = None
        self._navigator = None
        self._status_vars: dict[str, tk.StringVar] = {}
        self._stage_vars: dict[str, tk.BooleanVar] = {}

        # Garantir que as pastas de templates existam
        for sub in ("ui", "portal_menu", "stages"):
            (ROOT / "templates" / sub).mkdir(parents=True, exist_ok=True)

        self._build()
        self._refresh_all_status()
        self._start_game_monitor()

    # ── Construção da UI ────────────────────────────────────────────────────

    def _build(self):
        self._build_header()
        self._build_setup_section()
        self._build_automation_section()
        self._build_log_section()

    def _build_header(self):
        hdr = tk.Frame(self, bg=ACCENT, height=2)
        hdr.pack(fill="x")

        top = tk.Frame(self, bg=BG, pady=10)
        top.pack(fill="x", padx=16)

        tk.Label(top, text="🎮  TBH Task Bar Hero", font=("Segoe UI", 15, "bold"),
                 bg=BG, fg=WHITE).pack(side="left")

        right = tk.Frame(top, bg=BG)
        right.pack(side="right")

        tk.Label(right, text="Jogo:", font=FONT_S, bg=BG, fg=GRAY).pack(side="left", padx=(0, 4))
        self._game_dot = tk.Label(right, text="●", font=FONT_B, bg=BG, fg=RED)
        self._game_dot.pack(side="left")
        self._game_label = tk.Label(right, text="Não detectado", font=FONT_S, bg=BG, fg=RED)
        self._game_label.pack(side="left", padx=(2, 0))

        tk.Frame(self, bg=BG3, height=1).pack(fill="x")

    def _build_setup_section(self):
        self._setup_frame = tk.Frame(self, bg=BG, padx=16, pady=10)
        self._setup_frame.pack(fill="x")

        # ── Cabeçalho da seção ──────────────────────────────────────────────
        hdr = tk.Frame(self._setup_frame, bg=BG)
        hdr.pack(fill="x", pady=(0, 8))

        tk.Label(hdr, text="PASSO 1 — Configurar Reconhecimento Visual",
                 font=FONT_H, bg=BG, fg=ACCENT).pack(side="left")

        self._setup_summary = tk.Label(hdr, text="", font=FONT_S, bg=BG, fg=GRAY)
        self._setup_summary.pack(side="right")

        # ── Instrução ───────────────────────────────────────────────────────
        instr = tk.Frame(self._setup_frame, bg=BG2, padx=12, pady=8)
        instr.pack(fill="x", pady=(0, 10))

        tk.Label(instr,
                 text="ℹ️  Abra o jogo e o menu Portal. Clique em "
                      "[ Capturar ] e selecione o elemento indicado na tela.",
                 font=FONT_S, bg=BG2, fg=WHITE, wraplength=600, justify="left").pack(anchor="w")

        # ── Templates essenciais ────────────────────────────────────────────
        tk.Label(self._setup_frame, text="Elementos obrigatórios:",
                 font=FONT_B, bg=BG, fg=WHITE).pack(anchor="w", pady=(0, 4))

        req_grid = tk.Frame(self._setup_frame, bg=BG)
        req_grid.pack(fill="x", pady=(0, 8))

        for i, (name, subfolder, label, hint) in enumerate(REQUIRED_TEMPLATES):
            self._build_template_row(req_grid, i, name, subfolder, label, hint, required=True)

        # ── Templates de estágios ────────────────────────────────────────────
        sep = tk.Frame(self._setup_frame, bg=BG3, height=1)
        sep.pack(fill="x", pady=8)

        stage_hdr = tk.Frame(self._setup_frame, bg=BG)
        stage_hdr.pack(fill="x", pady=(0, 4))

        tk.Label(stage_hdr, text="Estágios (capture apenas os que for usar):",
                 font=FONT_B, bg=BG, fg=WHITE).pack(side="left")
        tk.Label(stage_hdr, text="→ Abra o Portal e role até o estágio desejado antes de capturar",
                 font=FONT_S, bg=BG, fg=GRAY).pack(side="left", padx=8)

        # Grade de 3 colunas para os estágios
        stage_grid = tk.Frame(self._setup_frame, bg=BG)
        stage_grid.pack(fill="x")

        for col in range(3):
            stage_grid.columnconfigure(col, weight=1)

        for idx, (name, stage_id) in enumerate(STAGE_TEMPLATES):
            row_i = idx // 3
            col_i = idx % 3
            hint = f"Botão do estágio {stage_id} dentro do menu Portal"
            self._build_stage_tile(stage_grid, row_i, col_i, name, stage_id, hint)

        tk.Frame(self, bg=BG3, height=1).pack(fill="x")

    def _build_template_row(self, parent, row, name, subfolder, label, hint, required=False):
        row_f = tk.Frame(parent, bg=BG2, padx=10, pady=6)
        row_f.pack(fill="x", pady=2)

        # Status icon
        sv = tk.StringVar(value="❌")
        self._status_vars[name] = sv
        status_lbl = tk.Label(row_f, textvariable=sv, font=("Segoe UI", 11),
                               bg=BG2, width=3)
        status_lbl.pack(side="left")

        # Nome e dica
        info = tk.Frame(row_f, bg=BG2)
        info.pack(side="left", fill="x", expand=True, padx=6)
        tk.Label(info, text=label, font=FONT_B, bg=BG2, fg=WHITE, anchor="w").pack(anchor="w")
        tk.Label(info, text=hint, font=FONT_S, bg=BG2, fg=GRAY, anchor="w").pack(anchor="w")

        # Botão capturar
        btn = tk.Button(
            row_f,
            text="📷  Capturar",
            font=FONT_S,
            bg=ACCENT, fg=WHITE,
            activebackground="#9d8ef9", activeforeground=WHITE,
            relief="flat", padx=10, pady=4, cursor="hand2",
            command=lambda n=name, s=subfolder, l=label, h=hint: self._capture_template(n, s, l, h),
        )
        btn.pack(side="right")

    def _build_stage_tile(self, parent, row, col, name, stage_id, hint):
        tile = tk.Frame(parent, bg=BG2, padx=8, pady=6)
        tile.grid(row=row, column=col, padx=3, pady=3, sticky="ew")

        sv = tk.StringVar(value="❌")
        self._status_vars[name] = sv

        left = tk.Frame(tile, bg=BG2)
        left.pack(side="left", fill="x", expand=True)

        top_row = tk.Frame(left, bg=BG2)
        top_row.pack(anchor="w")

        tk.Label(top_row, textvariable=sv, font=("Segoe UI", 10), bg=BG2).pack(side="left")
        tk.Label(top_row, text=f"  Estágio {stage_id}", font=FONT_B, bg=BG2, fg=WHITE).pack(side="left")

        btn = tk.Button(
            tile,
            text="📷",
            font=("Segoe UI", 9),
            bg=BG3, fg=WHITE,
            activebackground=ACCENT, activeforeground=WHITE,
            relief="flat", padx=6, pady=2, cursor="hand2",
            command=lambda n=name, sid=stage_id, h=hint: self._capture_template(
                n, "stages", f"Estágio {sid}", h
            ),
        )
        btn.pack(side="right")

    def _build_automation_section(self):
        self._auto_frame = tk.Frame(self, bg=BG, padx=16, pady=10)
        self._auto_frame.pack(fill="x")

        tk.Label(self._auto_frame, text="PASSO 2 — Automação de Mapas",
                 font=FONT_H, bg=BG, fg=ACCENT).pack(anchor="w", pady=(0, 10))

        body = tk.Frame(self._auto_frame, bg=BG)
        body.pack(fill="x")

        # ── Coluna esquerda: seleção de mapas ────────────────────────────────
        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(left, text="Selecione os mapas:", font=FONT_B, bg=BG, fg=WHITE).pack(anchor="w")

        list_frame = tk.Frame(left, bg=BG2)
        list_frame.pack(fill="both", expand=True, pady=(4, 0))

        yscroll = ttk.Scrollbar(list_frame, orient="vertical")
        self._stage_canvas = tk.Canvas(list_frame, bg=BG2, highlightthickness=0,
                                        yscrollcommand=yscroll.set, width=240, height=200)
        yscroll.config(command=self._stage_canvas.yview)
        self._stage_canvas.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        self._stage_inner = tk.Frame(self._stage_canvas, bg=BG2)
        self._stage_canvas.create_window((0, 0), window=self._stage_inner, anchor="nw")
        self._stage_inner.bind("<Configure>", lambda e: self._stage_canvas.configure(
            scrollregion=self._stage_canvas.bbox("all")))

        self._build_stage_checkboxes()

        # Botões de seleção rápida
        sel_row = tk.Frame(left, bg=BG)
        sel_row.pack(fill="x", pady=(4, 0))
        tk.Button(sel_row, text="Todos", font=FONT_S, bg=BG3, fg=WHITE,
                  relief="flat", padx=6, cursor="hand2",
                  command=self._select_all_stages).pack(side="left", padx=(0, 4))
        tk.Button(sel_row, text="Nenhum", font=FONT_S, bg=BG3, fg=WHITE,
                  relief="flat", padx=6, cursor="hand2",
                  command=self._deselect_all_stages).pack(side="left")

        # ── Coluna direita: presets ───────────────────────────────────────────
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="y", padx=(8, 0))

        tk.Label(right, text="Presets de farm:", font=FONT_B, bg=BG, fg=WHITE).pack(anchor="w")

        preset_box = tk.Frame(right, bg=BG2, padx=8, pady=8)
        preset_box.pack(fill="y", expand=True, pady=(4, 0))

        for key, (label, stages) in FARM_PRESETS.items():
            row = tk.Frame(preset_box, bg=BG2)
            row.pack(fill="x", pady=2)
            stages_str = ", ".join(stages)
            tk.Button(
                row,
                text=f"  {label}\n  ({stages_str})",
                font=FONT_S, bg=BG3, fg=WHITE,
                activebackground=ACCENT, activeforeground=WHITE,
                relief="flat", anchor="w", padx=8, pady=4, cursor="hand2",
                justify="left",
                command=lambda s=stages: self._apply_preset(s),
            ).pack(fill="x")

        # ── Controles de execução ────────────────────────────────────────────
        sep = tk.Frame(self._auto_frame, bg=BG3, height=1)
        sep.pack(fill="x", pady=10)

        ctrl = tk.Frame(self._auto_frame, bg=BG)
        ctrl.pack(fill="x")

        # Iterações
        iter_f = tk.Frame(ctrl, bg=BG)
        iter_f.pack(side="left", padx=(0, 16))

        tk.Label(iter_f, text="Repetições:", font=FONT_S, bg=BG, fg=GRAY).pack(anchor="w")
        self._iter_var = tk.StringVar(value="∞ Infinito")
        iter_opts = ["∞ Infinito", "1x", "3x", "5x", "10x", "25x", "50x"]
        iter_menu = ttk.Combobox(iter_f, textvariable=self._iter_var,
                                  values=iter_opts, state="readonly", width=12)
        iter_menu.pack()

        # Botões
        btn_f = tk.Frame(ctrl, bg=BG)
        btn_f.pack(side="left")

        self._start_btn = tk.Button(
            btn_f, text="▶  INICIAR FARM",
            font=("Segoe UI", 11, "bold"),
            bg=GREEN, fg="#1e1e2e",
            activebackground="#3dbb5e", activeforeground="#1e1e2e",
            relief="flat", padx=18, pady=8, cursor="hand2",
            command=self._on_start,
        )
        self._start_btn.pack(side="left", padx=(0, 8))

        self._once_btn = tk.Button(
            btn_f, text="→  Navegar uma vez",
            font=FONT, bg=BG3, fg=WHITE,
            activebackground=ACCENT, activeforeground=WHITE,
            relief="flat", padx=12, pady=8, cursor="hand2",
            command=self._on_navigate_once,
        )
        self._once_btn.pack(side="left", padx=(0, 8))

        self._stop_btn = tk.Button(
            btn_f, text="■  PARAR",
            font=("Segoe UI", 11, "bold"),
            bg=RED, fg=WHITE,
            activebackground="#cc4444", activeforeground=WHITE,
            relief="flat", padx=14, pady=8, cursor="hand2",
            state="disabled",
            command=self._on_stop,
        )
        self._stop_btn.pack(side="left")

        # Status de execução
        self._run_status = tk.Label(ctrl, text="", font=FONT_S, bg=BG, fg=YELLOW)
        self._run_status.pack(side="right")

        tk.Frame(self, bg=BG3, height=1).pack(fill="x")

    def _build_stage_checkboxes(self):
        acts = {
            "Act 1": [s for s in STAGE_TEMPLATES if s[1].startswith("1-")],
            "Act 2": [s for s in STAGE_TEMPLATES if s[1].startswith("2-")],
            "Act 3": [s for s in STAGE_TEMPLATES if s[1].startswith("3-")],
        }

        style = ttk.Style()
        style.configure("Stage.TCheckbutton", background=BG2, foreground=WHITE,
                         font=FONT_S, focuscolor=BG2)

        for act_label, stages in acts.items():
            tk.Label(self._stage_inner, text=f"  {act_label}",
                     font=FONT_B, bg=BG2, fg=ACCENT).pack(anchor="w", pady=(6, 2))

            for name, stage_id in stages:
                var = tk.BooleanVar(value=False)
                self._stage_vars[stage_id] = var
                cb = tk.Checkbutton(
                    self._stage_inner,
                    text=f"  Estágio {stage_id}",
                    variable=var,
                    bg=BG2, fg=WHITE,
                    selectcolor=ACCENT,
                    activebackground=BG2, activeforeground=WHITE,
                    font=FONT_S, anchor="w",
                )
                cb.pack(fill="x", padx=8)

    def _build_log_section(self):
        log_frame = tk.Frame(self, bg=BG, padx=16, pady=8)
        log_frame.pack(fill="both", expand=True)

        hdr = tk.Frame(log_frame, bg=BG)
        hdr.pack(fill="x", pady=(0, 4))

        tk.Label(hdr, text="📋  Log de Atividade", font=FONT_B, bg=BG, fg=WHITE).pack(side="left")
        tk.Button(hdr, text="Limpar", font=FONT_S, bg=BG3, fg=GRAY,
                  relief="flat", padx=6, cursor="hand2",
                  command=self._clear_log).pack(side="right")

        self._log = scrolledtext.ScrolledText(
            log_frame, height=8, font=MONO,
            bg=BG2, fg=WHITE, insertbackground=WHITE,
            state="disabled", relief="flat", padx=8, pady=6,
        )
        self._log.pack(fill="both", expand=True)

        self._log.tag_configure("ok",   foreground=GREEN)
        self._log.tag_configure("err",  foreground=RED)
        self._log.tag_configure("warn", foreground=ORANGE)
        self._log.tag_configure("info", foreground=WHITE)
        self._log.tag_configure("dim",  foreground=GRAY)

    # ── Captura de templates ────────────────────────────────────────────────

    def _capture_template(self, name: str, subfolder: str, label: str, hint: str):
        self._log_msg(f"Preparando captura: {label}...", "info")
        self.after(200, lambda: self._do_capture(name, subfolder, label, hint))

    def _do_capture(self, name: str, subfolder: str, label: str, hint: str):
        # Minimiza o bot para não aparecer na captura
        self.iconify()
        time.sleep(0.5)

        try:
            screenshot = take_screenshot()
        except Exception as e:
            self.deiconify()
            self._log_msg(f"Erro ao capturar tela: {e}", "err")
            return

        self.deiconify()

        # Abre o overlay de seleção
        overlay = CaptureOverlay(screenshot, hint=label)
        self.wait_window(overlay)

        if overlay.result is None:
            self._log_msg("Captura cancelada.", "warn")
            return

        x, y, w, h = overlay.result
        if w < 4 or h < 4:
            self._log_msg("Região muito pequena — tente novamente.", "warn")
            return

        crop = screenshot[y:y+h, x:x+w]
        path = template_path(name, subfolder)
        path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(path), crop)

        self._log_msg(f"✓ '{label}' salvo em templates/{subfolder}/{name}.png", "ok")
        self._refresh_all_status()

    # ── Status e monitoramento ──────────────────────────────────────────────

    def _refresh_all_status(self):
        ok_count = 0
        total_req = len(REQUIRED_TEMPLATES)

        for name, subfolder, *_ in REQUIRED_TEMPLATES:
            exists = template_exists(name, subfolder)
            self._status_vars[name].set("✅" if exists else "❌")
            if exists:
                ok_count += 1

        for name, _ in STAGE_TEMPLATES:
            exists = template_exists(name, "stages")
            self._status_vars[name].set("✅" if exists else "❌")

        self._setup_summary.config(
            text=f"{ok_count}/{total_req} essenciais prontos",
            fg=GREEN if ok_count == total_req else ORANGE,
        )

    def _start_game_monitor(self):
        def _monitor():
            while True:
                found = detect_game_window()
                color = GREEN if found else RED
                text = "Detectado ✓" if found else "Não detectado"
                self.after(0, lambda c=color, t=text: self._update_game_status(c, t))
                time.sleep(3)

        threading.Thread(target=_monitor, daemon=True).start()

    def _update_game_status(self, color: str, text: str):
        self._game_dot.config(fg=color)
        self._game_label.config(fg=color, text=text)

    # ── Lógica de automação ─────────────────────────────────────────────────

    def _get_navigator(self):
        if self._navigator is None:
            from tbh.config import Config
            from tbh import build_navigator
            config = Config.load(base_dir=ROOT)
            self._navigator = build_navigator(config)
            self._navigator.set_status_callback(lambda m: self._log_msg(m, "info"))
        return self._navigator

    def _get_selected_stages(self) -> list[str]:
        return [sid for sid, var in self._stage_vars.items() if var.get()]

    def _get_iterations(self) -> int | None:
        val = self._iter_var.get()
        if "∞" in val or "Infin" in val:
            return None
        try:
            return int(val.replace("x", ""))
        except ValueError:
            return None

    def _check_ready(self, stages: list[str]) -> str | None:
        missing_req = [
            label for name, subfolder, label, _ in REQUIRED_TEMPLATES
            if not template_exists(name, subfolder)
        ]
        if missing_req:
            return f"Templates obrigatórios faltando:\n• " + "\n• ".join(missing_req)

        missing_stages = [sid for sid in stages if not template_exists(f"stage_{sid.replace('-','_')}", "stages")]
        if missing_stages:
            return f"Capture os templates dos estágios:\n• " + "\n• ".join(missing_stages)

        return None

    def _on_start(self):
        stages = self._get_selected_stages()
        if not stages:
            messagebox.showwarning("Nenhum mapa", "Selecione pelo menos um estágio para iniciar.")
            return

        err = self._check_ready(stages)
        if err:
            messagebox.showerror("Configuração incompleta", err)
            return

        iters = self._get_iterations()
        desc = "∞" if iters is None else f"{iters}x"
        self._log_msg(f"Iniciando farm: {stages}  ({desc})", "ok")
        self._set_running(True)
        self._stop_event.clear()

        self._farm_thread = threading.Thread(
            target=self._run_farm, args=(stages, iters), daemon=True
        )
        self._farm_thread.start()

    def _on_navigate_once(self):
        stages = self._get_selected_stages()
        if len(stages) != 1:
            messagebox.showwarning("Seleção", "Selecione exatamente 1 estágio para 'Navegar uma vez'.")
            return

        err = self._check_ready(stages)
        if err:
            messagebox.showerror("Configuração incompleta", err)
            return

        self._set_running(True)
        self._stop_event.clear()
        threading.Thread(target=self._run_once, args=(stages[0],), daemon=True).start()

    def _on_stop(self):
        self._stop_event.set()
        self._log_msg("Parando após o ciclo atual...", "warn")
        self._set_running(False)

    def _run_farm(self, stages: list[str], iterations: int | None):
        try:
            nav = self._get_navigator()
            nav.farm_loop(stages, iterations=iterations, stop_event=self._stop_event)
        except Exception as e:
            self._log_msg(f"Erro: {e}", "err")
        finally:
            self.after(0, lambda: self._set_running(False))

    def _run_once(self, stage_id: str):
        try:
            nav = self._get_navigator()
            nav.navigate_to(stage_id)
        except Exception as e:
            self._log_msg(f"Erro: {e}", "err")
        finally:
            self.after(0, lambda: self._set_running(False))

    # ── Helpers de UI ───────────────────────────────────────────────────────

    def _set_running(self, running: bool):
        s_on  = "disabled" if running else "normal"
        s_off = "normal" if running else "disabled"
        self._start_btn.config(state=s_on)
        self._once_btn.config(state=s_on)
        self._stop_btn.config(state=s_off)
        self._run_status.config(text="⏳ Rodando..." if running else "")

    def _apply_preset(self, stage_ids: list[str]):
        for sid, var in self._stage_vars.items():
            var.set(sid in stage_ids)
        self._log_msg(f"Preset aplicado: {stage_ids}", "dim")

    def _select_all_stages(self):
        for var in self._stage_vars.values():
            var.set(True)

    def _deselect_all_stages(self):
        for var in self._stage_vars.values():
            var.set(False)

    def _log_msg(self, msg: str, tag: str = "info"):
        def _write():
            self._log.config(state="normal")
            ts = log_time()
            self._log.insert(tk.END, f"[{ts}]  ", "dim")
            self._log.insert(tk.END, msg + "\n", tag)
            self._log.see(tk.END)
            self._log.config(state="disabled")
            self._run_status.config(text=msg[:55] + ("…" if len(msg) > 55 else ""))
        self.after(0, _write)

    def _clear_log(self):
        self._log.config(state="normal")
        self._log.delete("1.0", tk.END)
        self._log.config(state="disabled")


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    if MISSING:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Dependências faltando",
            "Algumas bibliotecas não foram instaladas:\n\n" +
            "\n".join(MISSING) +
            "\n\nFeche este aviso e execute novamente o INICIAR.bat"
        )
        root.destroy()
        sys.exit(1)

    app = TBHBot()
    app.mainloop()


if __name__ == "__main__":
    main()
