# Arquivo: utils/system.py
import os
import time
import socket
import subprocess

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(f"Verificação de internet falhou: {ex}")
        return False

def fechar_processos_excel():
    """Força o fechamento de todos os processos EXCEL.EXE em execução."""
    print("Verificando e tentando fechar processos do Excel abertos...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "EXCEL.EXE"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Comando para fechar Excel executado.")
    except Exception as e:
        print(f"Não foi possível forçar o fechamento do Excel. Erro: {e}")
    time.sleep(2)

def limpar_pasta_downloads():
    """Apaga todos os arquivos na pasta de downloads."""
    print("Limpando a pasta de downloads...")
    caminho_script = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), __file__, '..')))
    pasta_downloads = os.path.join(caminho_script, "downloads")
    
    if not os.path.exists(pasta_downloads):
        os.makedirs(pasta_downloads)
        print("Pasta de downloads criada.")
        return

    for filename in os.listdir(pasta_downloads):
        file_path = os.path.join(pasta_downloads, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f'Falha ao deletar {file_path}. Razão: {e}')
    print("Pasta de downloads limpa.")