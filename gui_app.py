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
        self.check_vars = [] # Lista para guardar as variáveis e widgets dos checkboxes

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

    def _iniciar_automacao(self, callback_func, is_search=False, is_batch=False):
        debug_mode = self.debug_mode_var.get()
        self.stop_requested = False
        
        if is_search:
            ano_busca = self.search_ano_entry.get()
            if not ano_busca.isdigit() or not (2020 <= int(ano_busca) <= 2030):
                messagebox.showerror("Entrada Inválida", "Por favor, digite um ano válido.", parent=self.search_window)
                return
            
            self.search_button.config(state=tk.DISABLED)
            self.search_stop_button.config(state=tk.NORMAL)
            self.automation_thread = threading.Thread(target=callback_func, args=(ano_busca, self, debug_mode, self.update_search_results))
        
        elif is_batch:
            # Pega os dados da janela principal para usar no lote
            ano_str = self.ano_entry.get()
            mes_inicial = self.mes_inicial_combo.get()
            mes_final = self.mes_final_combo.get()
            
            lojas_selecionadas_com_widgets = []
            for var, chk_widget, loja_info in self.check_vars:
                if var.get():
                    lojas_selecionadas_com_widgets.append((chk_widget, loja_info))

            if not lojas_selecionadas_com_widgets:
                messagebox.showwarning("Nenhuma Loja", "Nenhuma loja foi selecionada para a automação.", parent=self.search_window)
                return

            # Desabilita botões em ambas as janelas
            self.start_button.config(state=tk.DISABLED)
            self.evolution_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.search_button.config(state=tk.DISABLED)
            self.search_stop_button.config(state=tk.NORMAL)
            
            self.automation_thread = threading.Thread(target=callback_func, args=(lojas_selecionadas_com_widgets, ano_str, mes_inicial, mes_final, self, debug_mode))
        
        else: # Automação individual
            loja_numero = self.loja_numero_entry.get()
            ano_str = self.ano_entry.get()
            mes_inicial = self.mes_inicial_combo.get()
            mes_final = self.mes_final_combo.get()

            # Validações...
            if not (loja_numero.isdigit() and ano_str.isdigit() and mes_inicial and mes_final):
                messagebox.showerror("Entrada Inválida", "Verifique se todos os campos estão preenchidos corretamente.")
                return

            self.start_button.config(state=tk.DISABLED)
            self.evolution_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.automation_thread = threading.Thread(target=callback_func, args=(loja_numero, ano_str, mes_inicial, mes_final, self, debug_mode))
        
        self.automation_thread.start()

    def iniciar_thread_automacao(self): self._iniciar_automacao(self.run_automation_callback)
    def iniciar_thread_evolucao(self): self._iniciar_automacao(self.run_evolution_callback)
    def iniciar_thread_busca(self): self._iniciar_automacao(self.run_search_callback, is_search=True)
    def iniciar_thread_lote(self): self._iniciar_automacao(self.run_batch_callback, is_batch=True)

    def solicitar_parada(self):
        if messagebox.askyesno("Confirmar Parada", "Tem certeza que deseja interromper a operação?"):
            self.status_label.config(text="Parada solicitada... Finalizando...")
            if self.search_window and self.search_window.winfo_exists():
                self.search_status_label.config(text="Parada solicitada... Finalizando...")
            self.stop_requested = True
            self.stop_button.config(state=tk.DISABLED)
            if self.search_window and self.search_window.winfo_exists():
                self.search_stop_button.config(state=tk.DISABLED)

    def atualizar_progresso(self, valor, maximo, texto_status, is_search=False):
        if self.stop_requested: return
        target_label = self.status_label
        target_bar = self.progress_bar

        if is_search and self.search_window and self.search_window.winfo_exists():
            target_label = self.search_status_label
            target_bar = self.search_progress_bar
        
        target_label.config(text=texto_status)
        target_bar['maximum'] = maximo
        target_bar['value'] = valor
        self.root.update_idletasks()

    def finalizar_automacao(self, sucesso=True, mensagem="", is_search=False):
        # Reabilita botões em ambas as janelas, se existirem
        self.start_button.config(state=tk.NORMAL)
        self.evolution_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.search_window and self.search_window.winfo_exists():
            self.search_button.config(state=tk.NORMAL)
            self.search_stop_button.config(state=tk.DISABLED)

        if self.stop_requested:
            msg = "Operação interrompida pelo usuário."
            self.status_label.config(text=msg)
            if is_search and self.search_window and self.search_window.winfo_exists():
                self.search_status_label.config(text=msg)
            return

        if sucesso:
            final_msg = mensagem or "Processo finalizado com sucesso!"
            if is_search:
                self.search_status_label.config(text=final_msg)
            else:
                self.status_label.config(text=final_msg)
                messagebox.showinfo("Sucesso", final_msg)
        else:
            error_msg = f"Erro: {mensagem}"
            if is_search and self.search_window and self.search_window.winfo_exists():
                self.search_status_label.config(text=error_msg)
                messagebox.showerror("Erro na Busca", mensagem, parent=self.search_window)
            else:
                self.status_label.config(text=error_msg)
                messagebox.showerror("Erro na Automação", mensagem)
    
    def set_automation_callbacks(self, full_callback, evolution_callback, search_callback, batch_callback):
        self.run_automation_callback = full_callback
        self.run_evolution_callback = evolution_callback
        self.run_search_callback = search_callback
        self.run_batch_callback = batch_callback

    def open_search_window(self):
        # ... (código para abrir a janela) ...
        if self.search_window and self.search_window.winfo_exists():
            self.search_window.focus()
            return

        self.search_window = tk.Toplevel(self.root)
        self.search_window.title("Buscar Lojas com Lançamentos")
        self.search_window.geometry("550x450")

        search_frame = ttk.Frame(self.search_window, padding="10")
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttk.Frame(search_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(top_frame, text="Ano:").pack(side=tk.LEFT, padx=5)
        self.search_ano_entry = ttk.Entry(top_frame, width=10)
        self.search_ano_entry.pack(side=tk.LEFT, padx=5)
        self.search_ano_entry.insert(0, str(datetime.now().year))
        
        self.search_button = ttk.Button(top_frame, text="Buscar", command=self.iniciar_thread_busca)
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.search_stop_button = ttk.Button(top_frame, text="Parar Busca", command=self.solicitar_parada, state=tk.DISABLED)
        self.search_stop_button.pack(side=tk.LEFT, padx=5)
        
        self.search_progress_bar = ttk.Progressbar(search_frame, orient="horizontal", length=300, mode="determinate")
        self.search_progress_bar.pack(pady=5, fill=tk.X)
        
        self.search_status_label = ttk.Label(search_frame, text="Pronto para buscar.")
        self.search_status_label.pack(pady=2)
        
        checklist_frame = ttk.Frame(search_frame)
        checklist_frame.pack(pady=(10, 0), fill=tk.BOTH, expand=True)
        
        select_frame = ttk.Frame(checklist_frame)
        select_frame.pack(fill=tk.X, pady=2)
        ttk.Button(select_frame, text="Selecionar Todos", command=self.selecionar_todos).pack(side=tk.LEFT)
        ttk.Button(select_frame, text="Limpar Seleção", command=self.limpar_todos).pack(side=tk.LEFT, padx=5)

        canvas = tk.Canvas(checklist_frame)
        scrollbar = ttk.Scrollbar(checklist_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        batch_button = ttk.Button(search_frame, text="Puxar Lançamentos Selecionados", command=self.iniciar_thread_lote)
        batch_button.pack(pady=10)

    def update_search_results(self, lojas):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.check_vars.clear()

        if lojas:
            for loja_info in lojas:
                var = tk.BooleanVar()
                # AQUI É A MUDANÇA PRINCIPAL
                texto_checkbox = f"{loja_info['loja_numero']} - {loja_info['fantasia']} ({loja_info['cnpj']}) - Lançamentos: {loja_info['lancamentos']}"
                chk = ttk.Checkbutton(self.scrollable_frame, 
                                      text=texto_checkbox,
                                      variable=var)
                chk.pack(anchor='w', padx=5)
                self.check_vars.append((var, chk, loja_info))
        else:
            ttk.Label(self.scrollable_frame, text="Nenhuma loja com lançamentos encontrada.").pack()
            
    def selecionar_todos(self):
        for var, _, _ in self.check_vars:
            var.set(True)
            
    def limpar_todos(self):
        for var, _, _ in self.check_vars:
            var.set(False)
            
    def marcar_loja_como_concluida(self, chk_widget):
        if chk_widget and chk_widget.winfo_exists():
            chk_widget.config(text=chk_widget.cget("text") + " - Concluído!", state=tk.DISABLED)
            self.root.update_idletasks()