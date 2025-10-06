# Arquivo: gui_app.py

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime

class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automação de Relatórios PAI")
        self.root.geometry("500x380")
        
        self.stop_requested = False
        self.automation_thread = None
        self.search_window = None

        self.meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

        self._create_menu()
        self._create_main_widgets()

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Buscar Lojas com Lançamentos", command=self.open_search_window)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

    def _create_main_widgets(self):
        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        frame_loja_ano = ttk.Frame(self.main_frame)
        frame_loja_ano.pack(pady=2)
        
        ttk.Label(frame_loja_ano, text="Número da Loja:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.loja_numero_entry = ttk.Entry(frame_loja_ano, width=20)
        self.loja_numero_entry.grid(row=0, column=1, padx=5, pady=2)
        self.loja_numero_entry.focus()
        
        ttk.Label(frame_loja_ano, text="Ano:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.ano_entry = ttk.Entry(frame_loja_ano, width=20)
        self.ano_entry.grid(row=1, column=1, padx=5, pady=2)
        self.ano_entry.insert(0, str(datetime.now().year))

        frame_periodo = ttk.Frame(self.main_frame)
        frame_periodo.pack(pady=10)

        ttk.Label(frame_periodo, text="Período Inicial:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.mes_inicial_combo = ttk.Combobox(frame_periodo, values=self.meses, width=17, state="readonly")
        self.mes_inicial_combo.grid(row=0, column=1, padx=5, pady=2)
        self.mes_inicial_combo.set("Jan")

        ttk.Label(frame_periodo, text="Período Final:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.mes_final_combo = ttk.Combobox(frame_periodo, values=self.meses, width=17, state="readonly")
        self.mes_final_combo.grid(row=1, column=1, padx=5, pady=2)
        self.mes_final_combo.set("Dez")

        self.debug_mode_var = tk.BooleanVar()
        self.debug_checkbutton = ttk.Checkbutton(
            self.main_frame,
            text="Executar em modo de depuração (navegador visível)",
            variable=self.debug_mode_var
        )
        self.debug_checkbutton.pack(pady=10)

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Iniciar Automação Completa", command=self.iniciar_thread_automacao)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.evolution_button = ttk.Button(button_frame, text="Evolução Mensal", command=self.iniciar_thread_evolucao)
        self.evolution_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Parar", command=self.solicitar_parada, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(self.main_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=5)

        self.status_label = ttk.Label(self.main_frame, text="Pronto para iniciar.")
        self.status_label.pack(pady=5)

    def _iniciar_automacao(self, callback_func, is_search=False):
        debug_mode = self.debug_mode_var.get()
        self.stop_requested = False
        
        if is_search:
            ano_busca = self.search_ano_entry.get()
            if not ano_busca.isdigit() or not (2020 <= int(ano_busca) <= 2030):
                messagebox.showerror("Entrada Inválida", "Por favor, digite um ano válido.", parent=self.search_window)
                return
            
            self.search_button.config(state=tk.DISABLED)
            self.search_stop_button.config(state=tk.NORMAL)
            self.search_results_text.delete('1.0', tk.END) # Limpa resultados anteriores
            self.automation_thread = threading.Thread(target=callback_func, args=(ano_busca, self, debug_mode, self.update_search_results))
        else:
            loja_numero = self.loja_numero_entry.get()
            ano_str = self.ano_entry.get()
            mes_inicial = self.mes_inicial_combo.get()
            mes_final = self.mes_final_combo.get()

            if not loja_numero.isdigit():
                messagebox.showerror("Entrada Inválida", "Por favor, digite um número de loja válido.")
                return
            if not ano_str.isdigit() or not (2020 <= int(ano_str) <= 2030):
                messagebox.showerror("Entrada Inválida", "Por favor, digite um ano válido.")
                return
            if mes_inicial not in self.meses or mes_final not in self.meses:
                messagebox.showerror("Entrada Inválida", "Por favor, selecione os meses.")
                return

            self.start_button.config(state=tk.DISABLED)
            self.evolution_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.automation_thread = threading.Thread(target=callback_func, args=(loja_numero, ano_str, mes_inicial, mes_final, self, debug_mode))
        
        self.automation_thread.start()

    def iniciar_thread_automacao(self):
        self._iniciar_automacao(self.run_automation_callback)

    def iniciar_thread_evolucao(self):
        self._iniciar_automacao(self.run_evolution_callback)
        
    def iniciar_thread_busca(self):
        self._iniciar_automacao(self.run_search_callback, is_search=True)

    def solicitar_parada(self):
        if messagebox.askyesno("Confirmar Parada", "Tem certeza que deseja interromper a operação?"):
            self.status_label.config(text="Parada solicitada... Finalizando...")
            if self.search_window:
                self.search_status_label.config(text="Parada solicitada... Finalizando...")
            self.stop_requested = True
            self.stop_button.config(state=tk.DISABLED)
            if self.search_window:
                self.search_stop_button.config(state=tk.DISABLED)

    def atualizar_progresso(self, valor, maximo, texto_status, is_search=False):
        if self.stop_requested: return

        if is_search and self.search_window:
            self.search_status_label.config(text=texto_status)
            self.search_progress_bar['maximum'] = maximo
            self.search_progress_bar['value'] = valor
        else:
            self.status_label.config(text=texto_status)
            self.progress_bar['maximum'] = maximo
            self.progress_bar['value'] = valor
        self.root.update_idletasks()

    def finalizar_automacao(self, sucesso=True, mensagem="", is_search=False):
        if is_search and self.search_window:
            self.search_button.config(state=tk.NORMAL)
            self.search_stop_button.config(state=tk.DISABLED)
            if self.stop_requested:
                self.search_status_label.config(text="Busca interrompida pelo usuário.")
            elif sucesso:
                self.search_status_label.config(text="Busca finalizada com sucesso!")
            else:
                self.search_status_label.config(text=f"Erro: {mensagem}")
                messagebox.showerror("Erro na Busca", mensagem, parent=self.search_window)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.evolution_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            if self.stop_requested:
                self.status_label.config(text="Automação interrompida pelo usuário.")
            elif sucesso:
                self.status_label.config(text="Processo finalizado com sucesso!")
                messagebox.showinfo("Sucesso", "Automação finalizada com sucesso!")
            else:
                self.status_label.config(text=f"Erro: {mensagem}")
                messagebox.showerror("Erro", mensagem)
    
    def set_automation_callbacks(self, full_callback, evolution_callback, search_callback):
        self.run_automation_callback = full_callback
        self.run_evolution_callback = evolution_callback
        self.run_search_callback = search_callback

    def open_search_window(self):
        if self.search_window and self.search_window.winfo_exists():
            self.search_window.focus()
            return

        self.search_window = tk.Toplevel(self.root)
        self.search_window.title("Buscar Lojas com Lançamentos")
        self.search_window.geometry("450x400")

        search_frame = ttk.Frame(self.search_window, padding="10")
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Widgets da nova janela ---
        top_frame = ttk.Frame(search_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(top_frame, text="Ano da Busca:").pack(side=tk.LEFT, padx=5)
        self.search_ano_entry = ttk.Entry(top_frame, width=10)
        self.search_ano_entry.pack(side=tk.LEFT, padx=5)
        self.search_ano_entry.insert(0, str(datetime.now().year))
        
        self.search_button = ttk.Button(top_frame, text="Buscar", command=self.iniciar_thread_busca)
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.search_stop_button = ttk.Button(top_frame, text="Parar", command=self.solicitar_parada, state=tk.DISABLED)
        self.search_stop_button.pack(side=tk.LEFT, padx=5)
        
        self.search_progress_bar = ttk.Progressbar(search_frame, orient="horizontal", length=300, mode="determinate")
        self.search_progress_bar.pack(pady=5)
        
        self.search_status_label = ttk.Label(search_frame, text="Pronto para buscar.")
        self.search_status_label.pack(pady=2)
        
        ttk.Label(search_frame, text="Lojas Encontradas:").pack(pady=(10, 2), anchor='w')
        self.search_results_text = scrolledtext.ScrolledText(search_frame, wrap=tk.WORD, height=10)
        self.search_results_text.pack(fill=tk.BOTH, expand=True)

    def update_search_results(self, lojas):
        self.search_results_text.delete('1.0', tk.END)
        if lojas:
            self.search_results_text.insert(tk.END, "\n".join(lojas))
        else:
            self.search_results_text.insert(tk.END, "Nenhuma loja com lançamentos encontrada para os filtros.")