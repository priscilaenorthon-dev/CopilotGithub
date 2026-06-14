import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from tbh import build_navigator
from tbh.config import Config
from tbh.navigator import NavigationError


class AutomationApp(tk.Tk):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.navigator = build_navigator(config)
        self.navigator.set_status_callback(self._append_log)
        self._stop_event = threading.Event()
        self._farm_thread: threading.Thread | None = None

        self.title("TBH: Task Bar Hero — Bot de Automação")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        # ── Top: Stage selector ──────────────────────────────────────────────
        selector_frame = ttk.LabelFrame(self, text="Selecionar Estágios", padding=8)
        selector_frame.grid(row=0, column=0, sticky="nsew", **pad)

        ttk.Label(selector_frame, text="Mapas disponíveis (Ctrl+Click para múltiplos):").grid(
            row=0, column=0, sticky="w"
        )

        list_frame = tk.Frame(selector_frame)
        list_frame.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.stage_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            width=28,
            height=14,
            font=("Courier", 10),
        )
        scrollbar.config(command=self.stage_listbox.yview)
        self.stage_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for act_key, act in self.config.acts.items():
            self.stage_listbox.insert(tk.END, f"── {act.label} ──")
            last_idx = self.stage_listbox.size() - 1
            self.stage_listbox.itemconfig(last_idx, fg="gray", selectbackground="white", selectforeground="gray")
            for stage in act.stages:
                self.stage_listbox.insert(tk.END, f"  {stage.id}  {stage.label}")

        # ── Presets ─────────────────────────────────────────────────────────
        preset_frame = ttk.LabelFrame(self, text="Presets de Farm", padding=8)
        preset_frame.grid(row=1, column=0, sticky="ew", **pad)

        ttk.Label(preset_frame, text="Preset:").grid(row=0, column=0, sticky="w")
        self.preset_var = tk.StringVar(value="-- Selecione --")
        preset_names = ["-- Selecione --"] + list(self.config.farm_presets.keys())
        self.preset_dropdown = ttk.Combobox(
            preset_frame, textvariable=self.preset_var, values=preset_names, state="readonly", width=20
        )
        self.preset_dropdown.grid(row=0, column=1, sticky="ew", padx=4)
        self.preset_dropdown.bind("<<ComboboxSelected>>", self._on_preset_selected)

        ttk.Label(preset_frame, text="Iterações (0 = infinito):").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.iterations_var = tk.IntVar(value=0)
        self.iterations_spin = ttk.Spinbox(
            preset_frame, from_=0, to=9999, textvariable=self.iterations_var, width=8
        )
        self.iterations_spin.grid(row=1, column=1, sticky="w", padx=4, pady=(6, 0))

        # ── Controls ─────────────────────────────────────────────────────────
        ctrl_frame = tk.Frame(self)
        ctrl_frame.grid(row=2, column=0, sticky="ew", **pad)

        self.start_btn = ttk.Button(ctrl_frame, text="▶  Iniciar", command=self._on_start)
        self.start_btn.pack(side="left", padx=(0, 4))

        self.stop_btn = ttk.Button(ctrl_frame, text="■  Parar", command=self._on_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 4))

        self.once_btn = ttk.Button(ctrl_frame, text="→  Navegar uma vez", command=self._on_navigate_once)
        self.once_btn.pack(side="left")

        self.status_var = tk.StringVar(value="Aguardando...")
        ttk.Label(ctrl_frame, textvariable=self.status_var, foreground="blue").pack(side="right")

        # ── Log ─────────────────────────────────────────────────────────────
        log_frame = ttk.LabelFrame(self, text="Log", padding=4)
        log_frame.grid(row=3, column=0, sticky="nsew", **pad)

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=10, width=60, state="disabled", font=("Courier", 9)
        )
        self.log_text.pack(fill="both", expand=True)

        ttk.Button(log_frame, text="Limpar log", command=self._clear_log).pack(anchor="e", pady=(2, 0))

    # ── Callbacks ────────────────────────────────────────────────────────────

    def _on_preset_selected(self, _event=None) -> None:
        preset_name = self.preset_var.get()
        if preset_name == "-- Selecione --":
            return
        stage_ids = self.config.get_farm_preset(preset_name)
        self.stage_listbox.selection_clear(0, tk.END)
        for i in range(self.stage_listbox.size()):
            text = self.stage_listbox.get(i).strip()
            stage_id = text.split()[0] if text and not text.startswith("─") else None
            if stage_id and stage_id in stage_ids:
                self.stage_listbox.selection_set(i)

    def _get_selected_stage_ids(self) -> list[str]:
        selected = []
        for idx in self.stage_listbox.curselection():
            text = self.stage_listbox.get(idx).strip()
            if text.startswith("─"):
                continue
            stage_id = text.split()[0]
            selected.append(stage_id)
        return selected

    def _on_start(self) -> None:
        stage_ids = self._get_selected_stage_ids()
        if not stage_ids:
            messagebox.showwarning("Nenhum estágio", "Selecione pelo menos um estágio para iniciar o farm.")
            return

        iterations = self.iterations_var.get() or None
        self._stop_event.clear()
        self._set_running(True)
        self._farm_thread = threading.Thread(
            target=self._run_farm, args=(stage_ids, iterations), daemon=True
        )
        self._farm_thread.start()

    def _on_stop(self) -> None:
        self._stop_event.set()
        self._append_log("Parando após o ciclo atual...")
        self._set_running(False)

    def _on_navigate_once(self) -> None:
        stage_ids = self._get_selected_stage_ids()
        if len(stage_ids) != 1:
            messagebox.showwarning("Seleção inválida", "Selecione exatamente um estágio para navegação única.")
            return
        self._stop_event.clear()
        self._set_running(True)
        threading.Thread(target=self._run_once, args=(stage_ids[0],), daemon=True).start()

    def _run_farm(self, stage_ids: list[str], iterations: int | None) -> None:
        try:
            self.navigator.farm_loop(stage_ids, iterations=iterations, stop_event=self._stop_event)
        except NavigationError as e:
            self._append_log(f"ERRO: {e}")
        except Exception as e:
            self._append_log(f"ERRO inesperado: {e}")
        finally:
            self.after(0, lambda: self._set_running(False))

    def _run_once(self, stage_id: str) -> None:
        try:
            self.navigator.navigate_to(stage_id)
        except NavigationError as e:
            self._append_log(f"ERRO: {e}")
        except Exception as e:
            self._append_log(f"ERRO inesperado: {e}")
        finally:
            self.after(0, lambda: self._set_running(False))

    # ── UI helpers ───────────────────────────────────────────────────────────

    def _set_running(self, running: bool) -> None:
        state_on = "disabled" if running else "normal"
        state_off = "normal" if running else "disabled"
        self.start_btn.config(state=state_on)
        self.once_btn.config(state=state_on)
        self.stop_btn.config(state=state_off)
        self.status_var.set("Rodando..." if running else "Aguardando...")

    def _append_log(self, msg: str) -> None:
        def _write():
            self.log_text.config(state="normal")
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state="disabled")
            self.status_var.set(msg[:60] + ("..." if len(msg) > 60 else ""))
        self.after(0, _write)

    def _clear_log(self) -> None:
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")
