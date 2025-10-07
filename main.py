# Arquivo: main.py
import ttkbootstrap as ttk
from view.app_controller import AppController
from utils.config import resource_path # Importe a função resource_path

if __name__ == "__main__":
    # 'litera' é um tema claro e profissional. Outras opções: 'flatly', 'journal', 'lumen', 'cosmo', 'superhero'
    root = ttk.Window(themename="litera")
    
    # --- NOVIDADE: Define o ícone da janela ---
    # A função resource_path garante que o ícone seja encontrado, não importa como a app seja executada
    root.iconbitmap(resource_path("assets/icone.ico"))
    
    app = AppController(root)
    root.mainloop()