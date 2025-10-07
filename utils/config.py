# Arquivo: utils/config.py
import json
from sys import exit

def carregar_configuracoes():
    """Carrega todas as configurações do config.json."""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validação para garantir que as chaves principais existem
        if 'database' not in config or 'login' not in config:
            raise KeyError
        
        return config

    except FileNotFoundError:
        exit("Erro: Arquivo de configuração 'config.json' não encontrado!")
    except KeyError:
        exit("Erro: O arquivo 'config.json' deve conter as chaves 'database' e 'login'.")
    except json.JSONDecodeError:
        exit("Erro: O arquivo 'config.json' possui um formato inválido.")

# Carrega as configurações uma vez para serem usadas em todo o projeto
_CONFIG = carregar_configuracoes()

# Exporta as seções de configuração para fácil importação em outros módulos
DB_CONFIG = _CONFIG['database']
LOGIN_CONFIG = _CONFIG['login']