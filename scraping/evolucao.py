# Arquivo: scraping/evolucao.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def stoppable_sleep(duration, gui_callback):
    """Uma função de espera que pode ser interrompida."""
    for i in range(duration):
        if gui_callback.stop_requested:
            raise InterruptedError("Parada solicitada durante a espera.")
        time.sleep(1)

def _selecionar_ano(driver, wait, ano_alvo_str, gui_callback):
    """Função auxiliar para navegar até o ano correto."""
    ano_alvo = int(ano_alvo_str)
    
    btn_ano_atual_xpath = "//div[contains(@class, 'toolbar')]//button[2]"
    btn_anterior_xpath = "//button[i[contains(@class, 'fa-chevron-left')]]"
    btn_proximo_xpath = "//button[i[contains(@class, 'fa-chevron-right')]]"

    for _ in range(10): 
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")

        ano_atual_elem = wait.until(EC.visibility_of_element_located((By.XPATH, btn_ano_atual_xpath)))
        ano_atual = int(ano_atual_elem.text)

        if ano_atual == ano_alvo:
            print(f"Ano {ano_alvo} selecionado.")
            return
        elif ano_atual > ano_alvo:
            print(f"Ano atual ({ano_atual}) > Alvo ({ano_alvo}). Clicando em 'Anterior'.")
            driver.find_element(By.XPATH, btn_anterior_xpath).click()
        else:
            print(f"Ano atual ({ano_atual}) < Alvo ({ano_alvo}). Clicando em 'Próximo'.")
            driver.find_element(By.XPATH, btn_proximo_xpath).click()
        
        stoppable_sleep(1, gui_callback)

    raise Exception(f"Não foi possível selecionar o ano {ano_alvo} após 10 tentativas.")

# --- FUNÇÃO CORRIGIDA ---
def executar_evolution_actions(driver, wait, cnpj_alvo, ano_inicial, mes_inicial, ano_final, mes_final, gui_callback):
    """
    Executa o processo de download da "Evolução Mensal".
    """
    print(f"\nINICIANDO PROCESSAMENTO DE EVOLUÇÃO MENSAL PARA O CNPJ: {cnpj_alvo} | Período: {mes_inicial}/{ano_inicial} a {mes_final}/{ano_final}")

    try:
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")

        gui_callback.atualizar_progresso(0, 100, "Filtrando para buscar relatório de evolução...")

        seletor_avaliacao_inicial = (By.XPATH, "//a[contains(., 'Avaliação')]")
        wait.until(EC.element_to_be_clickable(seletor_avaliacao_inicial)).click()
        stoppable_sleep(2, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Loja')]"))).click()
        stoppable_sleep(1, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Selecione...']]"))).click()
        stoppable_sleep(1, gui_callback)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Localizar']"))).send_keys(cnpj_alvo)
        stoppable_sleep(2, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'list-item') and contains(text(), '{cnpj_alvo}')]"))).click()
        stoppable_sleep(1, gui_callback)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click()
        stoppable_sleep(1, gui_callback)
        _selecionar_ano(driver, wait, ano_inicial, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space()='{mes_inicial}']"))).click()

        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click()
        stoppable_sleep(1, gui_callback)
        _selecionar_ano(driver, wait, ano_final, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space()='{mes_final}']"))).click()
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aplicar filtros')]"))).click()
        stoppable_sleep(3, gui_callback)

        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(25, 100, "Filtros aplicados. Consultando lançamentos...")

        seletor_botoes_consulta = (By.XPATH, "//button[@tooltip='Consultar Lançamentos']")
        wait.until(EC.presence_of_all_elements_located(seletor_botoes_consulta))[0].click()
        
        print("Aguardando tela carregar...")
        stoppable_sleep(5, gui_callback)

        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(50, 100, "Clicando na aba 'Evolução Mensal'...")

        seletor_evolucao_mensal = (By.XPATH, "//a[@id='tab-dados-evolucao-link']")
        wait.until(EC.element_to_be_clickable(seletor_evolucao_mensal)).click()
        
        print("Aguardando aba carregar...")
        stoppable_sleep(5, gui_callback)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click(); stoppable_sleep(1, gui_callback)
        _selecionar_ano(driver, wait, ano_inicial, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space()='{mes_inicial}']"))).click()

        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click(); stoppable_sleep(1, gui_callback)
        _selecionar_ano(driver, wait, ano_final, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space()='{mes_final}']"))).click()
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continuar')]"))).click()
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(75, 100, "Iniciando download do relatório de evolução...")
        
        print("Aguardando geração do relatório...")
        stoppable_sleep(20, gui_callback)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., ' Gerar Excel')]"))).click()
        print("Download da Evolução Mensal iniciado. Aguardando...")
        stoppable_sleep(15, gui_callback)

        gui_callback.atualizar_progresso(100, 100, "Download da Evolução Mensal concluído!")
        print("\nProcesso de download da Evolução Mensal finalizado.")

    except InterruptedError as e:
        print(f"Processo interrompido pelo usuário: {e}")
        raise e
    except Exception as e_geral:
        print(f"Ocorreu um erro GERAL ao processar a Evolução Mensal para o CNPJ {cnpj_alvo}: {e_geral}")
        raise e_geral