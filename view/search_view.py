# Arquivo: view/search_view.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class SearchView(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.title("Buscar Lojas com Lançamentos")
        self.geometry("550x450")

        self.check_vars = []
        self._create_widgets()

    def _create_widgets(self):
        search_frame = ttk.Frame(self, padding="10")
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttk.Frame(search_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(top_frame, text="Ano:").pack(side=tk.LEFT, padx=5)
        self.search_ano_entry = ttk.Entry(top_frame, width=10)
        self.search_ano_entry.pack(side=tk.LEFT, padx=5)
        self.search_ano_entry.insert(0, str(datetime.now().year))
        
        self.search_button = ttk.Button(top_frame, text="Buscar", command=self.controller.start_search)
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.search_stop_button = ttk.Button(top_frame, text="Parar Busca", command=self.controller.request_stop, state=tk.DISABLED)
        self.search_stop_button.pack(side=tk.LEFT, padx=5)
        
        self.search_progress_bar = ttk.Progressbar(search_frame, orient="horizontal", length=300, mode="determinate")
        self.search_progress_bar.pack(pady=5, fill=tk.X)
        
        self.search_status_label = ttk.Label(search_frame, text="Pronto para buscar.")
        self.search_status_label.pack(pady=2)
        
        checklist_frame = ttk.Frame(search_frame)
        checklist_frame.pack(pady=(10, 0), fill=tk.BOTH, expand=True)
        
        select_frame = ttk.Frame(checklist_frame)
        select_frame.pack(fill=tk.X, pady=2)
        ttk.Button(select_frame, text="Selecionar Todos", command=self.select_all).pack(side=tk.LEFT)
        ttk.Button(select_frame, text="Limpar Seleção", command=self.clear_all).pack(side=tk.LEFT, padx=5)

        canvas = tk.Canvas(checklist_frame)
        scrollbar = ttk.Scrollbar(checklist_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        batch_button = ttk.Button(search_frame, text="Puxar Lançamentos Selecionados", command=self.controller.start_batch_automation)
        batch_button.pack(pady=10)

    def update_results(self, lojas):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.check_vars.clear()

        if lojas:
            for loja_info in lojas:
                var = tk.BooleanVar()
                texto = f"{loja_info['loja_numero']} - {loja_info['fantasia']} ({loja_info['cnpj']}) - Lançamentos: {loja_info['lancamentos']}"
                chk = ttk.Checkbutton(self.scrollable_frame, text=texto, variable=var)
                chk.pack(anchor='w', padx=5)
                self.check_vars.append((var, chk, loja_info))
        else:
            ttk.Label(self.scrollable_frame, text="Nenhuma loja com lançamentos encontrada.").pack()

    def select_all(self):
        for var, _, _ in self.check_vars:
            var.set(True)
            
    def clear_all(self):
        for var, _, _ in self.check_vars:
            var.set(False)