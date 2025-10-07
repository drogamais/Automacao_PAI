# Arquivo: main.py
import ttkbootstrap as ttk
from view.app_controller import AppController

if __name__ == "__main__":
    # A janela principal agora é criada com um tema. 
    # 'litera' é um tema claro e profissional. Outras opções: 'flatly', 'journal', 'lumen', 'cosmo', 'superhero'
    root = ttk.Window(themename="litera")
    
    app = AppController(root)
    root.mainloop()