import json
import sys
import os
from sys import exit

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando em dev e no PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def carregar_configuracoes():
    """Carrega todas as configurações do config.json."""
    config_path = resource_path("config.json") # Usa a nova função para encontrar o arquivo
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'database' not in config or 'login' not in config:
            raise KeyError
        
        return config

    except FileNotFoundError:
        exit(f"Erro: Arquivo de configuração '{config_path}' não encontrado!")
    except KeyError:
        exit("Erro: O arquivo 'config.json' deve conter as chaves 'database' e 'login'.")
    except json.JSONDecodeError:
        exit("Erro: O arquivo 'config.json' possui um formato inválido.")

# Carrega as configurações uma vez para serem usadas em todo o projeto
_CONFIG = carregar_configuracoes()

DB_CONFIG = _CONFIG['database']
LOGIN_CONFIG = _CONFIG['login']