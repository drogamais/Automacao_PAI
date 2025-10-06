# Arquivo: step02_pai_evolution.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def executar_evolution_actions(driver, wait, cnpj_alvo, gui_callback):
    """
    Executa o processo de download da "Evolução Mensal".
    """
    print(f"\nINICIANDO PROCESSAMENTO DE EVOLUÇÃO MENSAL PARA O CNPJ: {cnpj_alvo}")

    try:
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")

        gui_callback.atualizar_progresso(0, 100, "Filtrando para buscar relatório de evolução...")

        # Navega até a avaliação e aplica os filtros
        seletor_avaliacao_inicial = (By.XPATH, "//a[contains(., 'Avaliação')]")
        wait.until(EC.element_to_be_clickable(seletor_avaliacao_inicial)).click()
        time.sleep(2)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Loja')]"))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Selecione...']]"))).click()
        time.sleep(1)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Localizar']"))).send_keys(cnpj_alvo)
        time.sleep(2)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'list-item') and contains(text(), '{cnpj_alvo}')]"))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Jan']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click()
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Dez']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aplicar filtros')]"))).click()
        time.sleep(3)

        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(25, 100, "Filtros aplicados. Consultando lançamentos...")

        # Clica no primeiro botão "Consultar Lançamentos"
        seletor_botoes_consulta = (By.XPATH, "//button[@tooltip='Consultar Lançamentos']")
        wait.until(EC.presence_of_all_elements_located(seletor_botoes_consulta))[0].click()
        time.sleep(5) # Espera a nova tela carregar

        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(50, 100, "Clicando na aba 'Evolução Mensal'...")

        # Clica na aba "Evolução Mensal"
        seletor_evolucao_mensal = (By.XPATH, "//a[@id='tab-dados-evolucao-link']")
        wait.until(EC.element_to_be_clickable(seletor_evolucao_mensal)).click()
        time.sleep(5) # Espera a aba carregar

        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click(); time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Jan']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click(); time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Dez']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continuar')]"))).click()
        

        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(75, 100, "Iniciando download do relatório de evolução...")
        time.sleep(20)
        # Clica para gerar o Excel
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., ' Gerar Excel')]"))).click()
        print("Download da Evolução Mensal iniciado. Aguardando...")
        time.sleep(15) # Tempo maior para garantir o download

        gui_callback.atualizar_progresso(100, 100, "Download da Evolução Mensal concluído!")
        print("\nProcesso de download da Evolução Mensal finalizado.")

    except InterruptedError as e:
        print(f"Processo interrompido pelo usuário: {e}")
        raise e
    except Exception as e_geral:
        print(f"Ocorreu um erro GERAL ao processar a Evolução Mensal para o CNPJ {cnpj_alvo}: {e_geral}")
        raise e_geral