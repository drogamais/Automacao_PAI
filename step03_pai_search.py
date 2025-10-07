# Arquivo: step03_pai_search.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

def stoppable_sleep(duration, gui_callback):
    """Uma função de espera que pode ser interrompida."""
    for i in range(duration):
        if gui_callback.stop_requested:
            raise InterruptedError("Parada solicitada durante a espera.")
        time.sleep(1)

def executar_busca_lojas(driver, wait, ano_alvo, gui_callback):
    """
    Navega até a tela de efetividade, filtra e extrai os CNPJs e a contagem de lançamentos das lojas.
    Retorna uma lista de dicionários, cada um contendo o CNPJ e o número de lançamentos.
    """
    try:
        print("Aguardando a página principal do PAI carregar completamente...")
        stoppable_sleep(5, gui_callback)

        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(0, 100, "Navegando para Relatórios de Efetividade...", is_search=True)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'menu-link') and .//span[text()='Relatórios']]"))).click()
        stoppable_sleep(1, gui_callback)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'menu-link') and .//span[text()='Rede']]"))).click()
        stoppable_sleep(1, gui_callback)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/relatorio/rede/efetividade']"))).click()
        print("Navegou para a página de Efetividade.")
        gui_callback.atualizar_progresso(25, 100, "Página de efetividade carregada. Aplicando filtros...", is_search=True)
        stoppable_sleep(3, gui_callback)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Selecione...']]"))).click()
        stoppable_sleep(1, gui_callback)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='list-item' and normalize-space()='Drogamais']"))).click()
        stoppable_sleep(1, gui_callback)

        select_element = wait.until(EC.presence_of_element_located((By.ID, 'input-select-0')))
        select = Select(select_element)
        select.select_by_value(ano_alvo)
        print(f"Ano {ano_alvo} selecionado.")
        stoppable_sleep(1, gui_callback)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Emitir')]"))).click()
        gui_callback.atualizar_progresso(50, 100, "Emitindo relatório... Aguardando resultados...", is_search=True)
        print("Aguardando a tabela de resultados carregar...")
        
        wait.until(EC.presence_of_element_located((By.XPATH, "//tbody")))
        stoppable_sleep(2, gui_callback)

        gui_callback.atualizar_progresso(75, 100, "Extraindo dados da tabela...", is_search=True)
        
        lojas_com_lancamentos = []
        linhas_tabela = driver.find_elements(By.XPATH, "//tbody/tr")
        
        if not linhas_tabela:
            print("Nenhuma loja encontrada na tabela de resultados.")
            return []

        print(f"Analisando {len(linhas_tabela)} lojas na tabela...")
        for linha in linhas_tabela:
            if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
            
            celulas = linha.find_elements(By.TAG_NAME, "td")
            
            if len(celulas) < 14:
                continue

            cnpj = celulas[0].text.strip()
            lancamentos = 0
            # Verifica as colunas dos meses (índices 2 a 13)
            for i in range(2, 14):
                if celulas[i].text.strip():
                    lancamentos += 1
            
            if lancamentos > 0:
                lojas_com_lancamentos.append({'cnpj': cnpj, 'lancamentos': lancamentos})

        gui_callback.atualizar_progresso(100, 100, "Busca finalizada!", is_search=True)
        return lojas_com_lancamentos

    except InterruptedError as e:
        print(f"Busca interrompida pelo usuário: {e}")
        raise e
    except Exception as e_geral:
        print(f"Ocorreu um erro GERAL durante a busca: {e_geral}")
        raise e_geral