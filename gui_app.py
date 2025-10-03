# Arquivo: gui_app.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading

class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automação de Relatórios PAI")
        self.root.geometry("400x280") # Aumentei a altura para o novo campo
        
        self.stop_requested = False
        self.automation_thread = None

        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.main_frame, text="Digite o número da loja:").pack(pady=5)
        self.loja_numero_entry = ttk.Entry(self.main_frame, width=30)
        self.loja_numero_entry.pack(pady=5)
        self.loja_numero_entry.focus()

        # --- NOVO: Checkbox para o modo de depuração ---
        self.debug_mode_var = tk.BooleanVar()
        self.debug_checkbutton = ttk.Checkbutton(
            self.main_frame,
            text="Executar em modo de depuração (navegador visível)",
            variable=self.debug_mode_var
        )
        self.debug_checkbutton.pack(pady=10)

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        self.start_button = ttk.Button(button_frame, text="Iniciar Automação", command=self.iniciar_thread_automacao)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Parar", command=self.solicitar_parada, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(self.main_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=5)

        self.status_label = ttk.Label(self.main_frame, text="Pronto para iniciar.")
        self.status_label.pack(pady=5)

    def iniciar_thread_automacao(self):
        loja_numero = self.loja_numero_entry.get()
        if not loja_numero.isdigit():
            messagebox.showerror("Entrada Inválida", "Por favor, digite um número de loja válido.")
            return
        
        # --- NOVO: Captura o valor do checkbox ---
        debug_mode = self.debug_mode_var.get()
        
        self.stop_requested = False
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        
        # Passa o 'debug_mode' como argumento para a thread
        self.automation_thread = threading.Thread(target=self.run_automation_callback, args=(loja_numero, self, debug_mode))
        self.automation_thread.start()

    def solicitar_parada(self):
        # (Esta função continua igual)
        if messagebox.askyesno("Confirmar Parada", "Tem certeza que deseja interromper a automação?"):
            self.status_label.config(text="Parada solicitada... Finalizando tarefa atual...")
            self.stop_requested = True
            self.stop_button.config(state=tk.DISABLED)

    def atualizar_progresso(self, valor, maximo, texto_status):
        # (Esta função continua igual)
        if self.stop_requested: return
        self.status_label.config(text=texto_status)
        self.progress_bar['maximum'] = maximo
        self.progress_bar['value'] = valor
        self.root.update_idletasks()

    def finalizar_automacao(self, sucesso=True, mensagem=""):
        # (Esta função continua igual)
        self.start_button.config(state=tk.NORMAL)
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

    def set_automation_callback(self, callback):
        # (Esta função continua igual)
        self.run_automation_callback = callback