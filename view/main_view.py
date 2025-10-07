# Arquivo: view/main_view.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class MainView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10 10 10 10")
        self.parent = parent
        self.controller = controller

        # Configura o menu
        self._create_menu()

        # Variáveis
        self.meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        self.debug_mode_var = tk.BooleanVar()

        # Cria os widgets
        self._create_widgets()

    def _create_menu(self):
        menubar = tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Buscar Lojas com Lançamentos", command=self.controller.open_search_window)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.parent.quit)

    def _create_widgets(self):
        frame_loja_ano = ttk.Frame(self)
        frame_loja_ano.pack(pady=2)
        
        ttk.Label(frame_loja_ano, text="Número da Loja:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.loja_numero_entry = ttk.Entry(frame_loja_ano, width=20)
        self.loja_numero_entry.grid(row=0, column=1, padx=5, pady=2)
        self.loja_numero_entry.focus()
        
        ttk.Label(frame_loja_ano, text="Ano:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.ano_entry = ttk.Entry(frame_loja_ano, width=20)
        self.ano_entry.grid(row=1, column=1, padx=5, pady=2)
        self.ano_entry.insert(0, str(datetime.now().year))

        frame_periodo = ttk.Frame(self)
        frame_periodo.pack(pady=10)

        ttk.Label(frame_periodo, text="Período Inicial:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.mes_inicial_combo = ttk.Combobox(frame_periodo, values=self.meses, width=17, state="readonly")
        self.mes_inicial_combo.grid(row=0, column=1, padx=5, pady=2)
        self.mes_inicial_combo.set("Jan")

        ttk.Label(frame_periodo, text="Período Final:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.mes_final_combo = ttk.Combobox(frame_periodo, values=self.meses, width=17, state="readonly")
        self.mes_final_combo.grid(row=1, column=1, padx=5, pady=2)
        self.mes_final_combo.set("Dez")

        self.debug_checkbutton = ttk.Checkbutton(
            self,
            text="Executar em modo de depuração (navegador visível)",
            variable=self.debug_mode_var
        )
        self.debug_checkbutton.pack(pady=10)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Iniciar Automação Completa", command=self.controller.start_full_automation)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.evolution_button = ttk.Button(button_frame, text="Evolução Mensal", command=self.controller.start_evolution_automation)
        self.evolution_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Parar", command=self.controller.request_stop, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=5)

        self.status_label = ttk.Label(self, text="Pronto para iniciar.")
        self.status_label.pack(pady=5)