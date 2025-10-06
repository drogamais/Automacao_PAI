# Arquivo: gui_app.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automação de Relatórios PAI")
        self.root.geometry("500x380") # Aumentei a altura para os novos campos
        
        self.stop_requested = False
        self.automation_thread = None

        # --- Dicionário de Meses ---
        self.meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Frame para Loja e Ano ---
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

        # --- Frame para Período ---
        frame_periodo = ttk.Frame(self.main_frame)
        frame_periodo.pack(pady=10)

        ttk.Label(frame_periodo, text="Período Inicial:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.mes_inicial_combo = ttk.Combobox(frame_periodo, values=self.meses, width=17)
        self.mes_inicial_combo.grid(row=0, column=1, padx=5, pady=2)
        self.mes_inicial_combo.set("Jan") # Valor padrão

        ttk.Label(frame_periodo, text="Período Final:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.mes_final_combo = ttk.Combobox(frame_periodo, values=self.meses, width=17)
        self.mes_final_combo.grid(row=1, column=1, padx=5, pady=2)
        self.mes_final_combo.set("Dez") # Valor padrão

        # --- Checkbox de Depuração ---
        self.debug_mode_var = tk.BooleanVar()
        self.debug_checkbutton = ttk.Checkbutton(
            self.main_frame,
            text="Executar em modo de depuração (navegador visível)",
            variable=self.debug_mode_var
        )
        self.debug_checkbutton.pack(pady=10)

        # --- Botões de Ação ---
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

    def _iniciar_automacao(self, callback_func):
        loja_numero = self.loja_numero_entry.get()
        if not loja_numero.isdigit():
            messagebox.showerror("Entrada Inválida", "Por favor, digite um número de loja válido.")
            return

        ano_str = self.ano_entry.get()
        if not ano_str.isdigit() or not (2020 <= int(ano_str) <= 2030):
            messagebox.showerror("Entrada Inválida", "Por favor, digite um ano válido (entre 2020 e 2030).")
            return

        mes_inicial = self.mes_inicial_combo.get()
        mes_final = self.mes_final_combo.get()
        if mes_inicial not in self.meses or mes_final not in self.meses:
            messagebox.showerror("Entrada Inválida", "Por favor, selecione um mês inicial e final válidos.")
            return

        debug_mode = self.debug_mode_var.get()
        
        self.stop_requested = False
        self.start_button.config(state=tk.DISABLED)
        self.evolution_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        
        self.automation_thread = threading.Thread(target=callback_func, args=(loja_numero, ano_str, mes_inicial, mes_final, self, debug_mode))
        self.automation_thread.start()

    def iniciar_thread_automacao(self):
        self._iniciar_automacao(self.run_automation_callback)

    def iniciar_thread_evolucao(self):
        self._iniciar_automacao(self.run_evolution_callback)

    def solicitar_parada(self):
        if messagebox.askyesno("Confirmar Parada", "Tem certeza que deseja interromper a automação?"):
            self.status_label.config(text="Parada solicitada... Finalizando tarefa atual...")
            self.stop_requested = True
            self.stop_button.config(state=tk.DISABLED)

    def atualizar_progresso(self, valor, maximo, texto_status):
        if self.stop_requested: return
        self.status_label.config(text=texto_status)
        self.progress_bar['maximum'] = maximo
        self.progress_bar['value'] = valor
        self.root.update_idletasks()

    def finalizar_automacao(self, sucesso=True, mensagem=""):
        self.start_button.config(state=tk.NORMAL)
        self.evolution_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if self.stop_requested:
            self.status_label.config(text="Automação interrompida pelo usuário.")
            return

        if sucesso:
            self.status_label.config(text="Processo finalizado com sucesso!")
            messagebox.showinfo("Sucesso", "Automação finalizada com sucesso!")
        else:
            self.status_label.config(text=f"Erro: {mensagem}")
            messagebox.showerror("Erro", mensagem)

    def set_automation_callbacks(self, full_callback, evolution_callback):
        self.run_automation_callback = full_callback
        self.run_evolution_callback = evolution_callback