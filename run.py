# Arquivo: run.py (O Orquestrador Principal)

import os
import time
import tkinter as tk
import mariadb
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from gui_app import AutomationGUI
import step01_login_actions
import step02_pai_actions
import step02_pai_evolution

# Importa todos os scripts de processamento
import processar_financeiro
import processar_performance
import processar_evolucao_financeiro
import processar_evolucao_performance


# --- CONFIGURAÇÕES ---
DB_USER = "drogamais"
DB_PASSWORD = "dB$MYSql@2119"
DB_HOST = "10.48.12.20"
DB_PORT = 3306
DB_NAME = "dbDrogamais"

def buscar_cnpj_no_banco(loja_numero):
    conn = None
    try:
        conn = mariadb.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()
        query = "SELECT cnpj FROM bronze_lojas WHERE loja_numero = ?"
        cursor.execute(query, (loja_numero,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    finally:
        if conn: conn.close()

def setup_driver(debug_mode):
    caminho_script = os.path.dirname(os.path.realpath(__file__))
    pasta_downloads = os.path.join(caminho_script, "downloads")
    if not os.path.exists(pasta_downloads):
        os.makedirs(pasta_downloads)

    chrome_options = Options()
    prefs = {
        "download.default_directory": pasta_downloads,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    chrome_options.add_experimental_option("prefs", prefs)

    if not debug_mode:
        print("Iniciando em modo oculto (headless)...")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
    else:
        print("Iniciando em modo de depuração (navegador visível com DevTools)...")
        chrome_options.add_argument("--auto-open-devtools-for-tabs")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    if debug_mode:
        driver.maximize_window()
        
    return driver

def executar_workflow_completo(loja_numero, gui_callback, debug_mode):
    driver = None
    try:
        gui_callback.atualizar_progresso(0, 100, f"Buscando CNPJ para a loja {loja_numero}...")
        cnpj_selecionado = buscar_cnpj_no_banco(loja_numero)
        if not cnpj_selecionado:
            raise ValueError(f"Loja {loja_numero} não encontrada.")
        
        gui_callback.atualizar_progresso(0, 100, f"CNPJ {cnpj_selecionado} encontrado. Iniciando navegador...")
        driver = setup_driver(debug_mode)
        wait = WebDriverWait(driver, 60)
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(0, 100, "Realizando login...")
        step01_login_actions.login_e_navega_para_pai(driver, wait)
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        step02_pai_actions.executar_acoes_pai(driver, wait, cnpj_selecionado, gui_callback)
        
        if driver: driver.quit()

        # --- SEÇÃO DE PROCESSAMENTO PARA AUTOMAÇÃO COMPLETA ---
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(0, 100, "Processando planilhas de Financeiro...")
        processar_financeiro.main()

        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(50, 100, "Processando planilhas de Performance...")
        processar_performance.main()
        
        if not gui_callback.stop_requested:
            gui_callback.finalizar_automacao(sucesso=True)

    except InterruptedError as e:
        print(f"Processo interrompido pelo usuário: {e}")
        if driver: driver.quit()
        gui_callback.finalizar_automacao()
    except Exception as e:
        print(f"\nOcorreu um erro fatal na execução: {e}")
        if driver: 
            driver.save_screenshot("erro_screenshot_fatal.png")
            driver.quit()
        if not gui_callback.stop_requested:
            gui_callback.finalizar_automacao(sucesso=False, mensagem=f"Erro fatal: {e}")

def executar_workflow_evolucao(loja_numero, gui_callback, debug_mode):
    driver = None
    try:
        gui_callback.atualizar_progresso(0, 100, f"Buscando CNPJ para a loja {loja_numero}...")
        cnpj_selecionado = buscar_cnpj_no_banco(loja_numero)
        if not cnpj_selecionado:
            raise ValueError(f"Loja {loja_numero} não encontrada.")

        gui_callback.atualizar_progresso(0, 100, f"CNPJ {cnpj_selecionado} encontrado. Iniciando navegador...")
        driver = setup_driver(debug_mode)
        wait = WebDriverWait(driver, 60)
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(0, 100, "Realizando login...")
        step01_login_actions.login_e_navega_para_pai(driver, wait)
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        step02_pai_evolution.executar_evolution_actions(driver, wait, cnpj_selecionado, gui_callback)
        
        if driver: driver.quit()

        # --- SEÇÃO DE PROCESSAMENTO PARA EVOLUÇÃO MENSAL ---
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(0, 100, "Processando Evolução Financeira...")
        processar_evolucao_financeiro.main()

        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(50, 100, "Processando Evolução de Performance...")
        processar_evolucao_performance.main()
        
        if not gui_callback.stop_requested:
            gui_callback.finalizar_automacao(sucesso=True, mensagem="Downloads e processamentos de Evolução concluídos.")

    except InterruptedError as e:
        print(f"Processo interrompido pelo usuário: {e}")
        if driver: driver.quit()
        gui_callback.finalizar_automacao()
    except Exception as e:
        print(f"\nOcorreu um erro fatal na execução da Evolução Mensal: {e}")
        if driver:
            driver.save_screenshot("erro_screenshot_fatal_evolucao.png")
            driver.quit()
        if not gui_callback.stop_requested:
            gui_callback.finalizar_automacao(sucesso=False, mensagem=f"Erro fatal na Evolução Mensal: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AutomationGUI(root)
    app.set_automation_callbacks(executar_workflow_completo, executar_workflow_evolucao)
    root.mainloop()