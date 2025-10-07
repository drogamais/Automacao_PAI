# Arquivo: view/search_view.py
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from datetime import datetime

class SearchView(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.title("Buscar Lojas com Lançamentos")
        self.geometry("500x550")

        self.check_vars = []
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttkb.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttkb.LabelFrame(main_frame, text="Filtros", padding="10")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttkb.Label(top_frame, text="Ano:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_ano_entry = ttkb.Entry(top_frame, width=10)
        self.search_ano_entry.pack(side=tk.LEFT, padx=5)
        self.search_ano_entry.insert(0, str(datetime.now().year))
        
        self.search_button = ttkb.Button(top_frame, text="Buscar", command=self.controller.start_search, bootstyle="primary")
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.search_stop_button = ttkb.Button(top_frame, text="Parar Busca", command=self.controller.request_stop, state=tk.DISABLED, bootstyle="danger-outline")
        self.search_stop_button.pack(side=tk.LEFT, padx=5)
        
        self.search_progress_bar = ttkb.Progressbar(top_frame, orient="horizontal", mode="determinate")
        self.search_progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        self.search_status_label = ttkb.Label(main_frame, text="Pronto para buscar.")
        self.search_status_label.pack(pady=5, fill=tk.X)
        
        results_frame = ttkb.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        select_frame = ttkb.Frame(results_frame)
        select_frame.pack(fill=tk.X, pady=2)
        ttkb.Button(select_frame, text="Selecionar Todos", command=self.select_all).pack(side=tk.LEFT)
        ttkb.Button(select_frame, text="Limpar Seleção", command=self.clear_all).pack(side=tk.LEFT, padx=5)

        canvas_frame = ttkb.Frame(results_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(5,0))
        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttkb.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview, bootstyle="round")
        self.scrollable_frame = ttkb.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        batch_button = ttkb.Button(main_frame, text="Puxar Lançamentos Selecionados", command=self.controller.start_batch_automation, bootstyle="success")
        batch_button.pack(pady=(10,0), fill=tk.X)

    def update_results(self, lojas):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.check_vars.clear()

        if lojas:
            for loja_info in lojas:
                var = tk.BooleanVar()
                texto = f"{loja_info['loja_numero']} - {loja_info['fantasia']} ({loja_info['cnpj']}) - Lançamentos: {loja_info['lancamentos']}"
                chk = ttkb.Checkbutton(self.scrollable_frame, text=texto, variable=var)
                chk.pack(anchor='w', padx=5, pady=2)
                self.check_vars.append((var, chk, loja_info))
        else:
            ttkb.Label(self.scrollable_frame, text="Nenhuma loja com lançamentos encontrada.").pack(padx=5, pady=5)

    def select_all(self):
        for var, _, _ in self.check_vars:
            var.set(True)
            
    def clear_all(self):
        for var, _, _ in self.check_vars:
            var.set(False)