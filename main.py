# Arquivo: main.py
import ttkbootstrap as ttk
from view.view_logic import AppController
from utils.config import resource_path
import sys
import os
from datetime import datetime

class Logger:
    def __init__(self, filename="automacao_pai.log"):
        self.terminal = sys.stdout  # Guarda o terminal original (pode ser None)
        self.log_path = os.path.join(os.path.abspath("."), filename)
        # Abre o arquivo de log em modo de escrita para sobrescrevê-lo
        self.log = open(self.log_path, "w", encoding='utf-8')

    def write(self, message):
        # --- CORREÇÃO AQUI ---
        # Só escreve no terminal se ele existir (não for None)
        if self.terminal:
            self.terminal.write(message)

        # Sempre escreve no arquivo de log
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.write(f"[{timestamp}] {message}")
        self.flush()

    def flush(self):
        # --- CORREÇÃO AQUI ---
        # Só faz o flush do terminal se ele existir
        if self.terminal:
            self.terminal.flush()
        self.log.flush()

    def __getattr__(self, attr):
        # Delega outras chamadas ao objeto terminal, se ele existir
        return getattr(self.terminal, attr)

if __name__ == "__main__":
    # Redireciona a saída padrão (stdout) e erros (stderr) para a nossa classe Logger
    sys.stdout = Logger()
    sys.stderr = sys.stdout

    print("--- INICIANDO APLICAÇÃO ---")

    root = ttk.Window(themename="litera")
    
    root.iconbitmap(resource_path("assets/icone.ico"))
    
    app = AppController(root)
    root.mainloop()

    print("--- APLICAÇÃO FINALIZADA ---")