# Arquivo: view/main_view.py
import tkinter as tk
from tkinter import ttk 
import ttkbootstrap as ttkb 
from datetime import datetime

class MainView(ttkb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="15 15 15 15")
        self.parent = parent
        self.controller = controller

        # --- CORREÇÃO AQUI ---
        # Variáveis movidas para o início do __init__
        self.meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        self.debug_mode_var = tk.BooleanVar()

        # Agora, chame os métodos que constroem a interface
        self._create_menu()
        self._create_widgets()

    def _create_menu(self):
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Buscar Lojas com Lançamentos", command=self.controller.open_search_window)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.parent.quit)

        # Menu Opções
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opções", menu=options_menu)
        options_menu.add_checkbutton(
            label="Executar em modo de depuração (navegador visível)",
            variable=self.debug_mode_var
        )

    def _create_widgets(self):
        # --- Grupo de Controles ---
        controls_frame = ttkb.LabelFrame(self, text="Controles de Automação", padding="10 10 10 10")
        controls_frame.pack(fill=tk.X, expand=True, pady=5)

        ttkb.Label(controls_frame, text="Número da Loja:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.loja_numero_entry = ttkb.Entry(controls_frame, width=25)
        self.loja_numero_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.loja_numero_entry.focus()
        
        ttkb.Label(controls_frame, text="Ano:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ano_entry = ttkb.Entry(controls_frame, width=25)
        self.ano_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.ano_entry.insert(0, str(datetime.now().year))

        ttkb.Label(controls_frame, text="Período Inicial:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.mes_inicial_combo = ttkb.Combobox(controls_frame, values=self.meses, width=22, state="readonly")
        self.mes_inicial_combo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.mes_inicial_combo.set("Jan")

        ttkb.Label(controls_frame, text="Período Final:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.mes_final_combo = ttkb.Combobox(controls_frame, values=self.meses, width=22, state="readonly")
        self.mes_final_combo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.mes_final_combo.set("Dez")
        
        controls_frame.columnconfigure(1, weight=1)

        # --- Grupo de Ações ---
        action_frame = ttkb.LabelFrame(self, text="Ações", padding="10 10 10 10")
        action_frame.pack(fill=tk.X, expand=True, pady=10)
        action_frame.columnconfigure((0, 1, 2), weight=1) # Faz os botões se expandirem

        self.start_button = ttkb.Button(action_frame, text="Extração Completa", command=self.controller.start_full_automation, bootstyle="primary")
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.evolution_button = ttkb.Button(action_frame, text="Evolução Mensal", command=self.controller.start_evolution_automation)
        self.evolution_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.stop_button = ttkb.Button(action_frame, text="Parar", command=self.controller.request_stop, state=tk.DISABLED, bootstyle="danger-outline")
        self.stop_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # --- Grupo de Status ---
        status_frame = ttkb.LabelFrame(self, text="Status", padding="10 10 10 10")
        status_frame.pack(fill=tk.X, expand=True)

        self.progress_bar = ttkb.Progressbar(status_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=5, fill=tk.X, expand=True)

        self.status_label = ttkb.Label(status_frame, text="Pronto para iniciar.", anchor="center")
        self.status_label.pack(pady=5, fill=tk.X, expand=True)