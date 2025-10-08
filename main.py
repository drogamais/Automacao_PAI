# Arquivo: main.py
import ttkbootstrap as ttk
from view.view_logic import AppController
from utils.config import resource_path
import sys
import os
from datetime import datetime

class Logger:
    def __init__(self, filename="automacao_pai.log"):
        self.terminal = sys.stdout
        # Garante que o log seja salvo no mesmo diretório do executável
        self.log_path = os.path.join(os.path.abspath("."), filename)
        # Abre o arquivo em modo de escrita para sobrescrever
        self.log = open(self.log_path, "w", encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        # Adiciona data e hora a cada linha do log
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.write(f"[{timestamp}] {message}")
        self.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def __getattr__(self, attr):
        return getattr(self.terminal, attr)

if __name__ == "__main__":
    # Redireciona a saída padrão para o nosso logger
    sys.stdout = Logger()
    sys.stderr = sys.stdout # Redireciona erros para o mesmo log

    print("--- INICIANDO APLICAÇÃO ---")

    root = ttk.Window(themename="litera")
    
    root.iconbitmap(resource_path("assets/icone.ico"))
    
    app = AppController(root)
    root.mainloop()

    print("--- APLICAÇÃO FINALIZADA ---")