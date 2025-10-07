# Arquivo: scraping/relatorios.py

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

def executar_acoes_pai(driver, wait, cnpj_alvo, ano_alvo, mes_inicial, mes_final, gui_callback):
    """
    Executa o processo de download com ano e meses dinâmicos.
    """
    print(f"\nINICIANDO PROCESSAMENTO PARA O CNPJ: {cnpj_alvo} | Período: {mes_inicial}/{ano_alvo} a {mes_final}/{ano_alvo}")
    
    try:
        def aplicar_filtros_completos():
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Avaliação')]"))).click(); stoppable_sleep(2, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Loja')]"))).click(); stoppable_sleep(1, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Selecione...']]"))).click(); stoppable_sleep(1, gui_callback)
            wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Localizar']"))).send_keys(cnpj_alvo); stoppable_sleep(2, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'list-item') and contains(text(), '{cnpj_alvo}')]"))).click(); stoppable_sleep(1, gui_callback)
            
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click(); stoppable_sleep(1, gui_callback)
            _selecionar_ano(driver, wait, ano_alvo, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space()='{mes_inicial}']"))).click()
            
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click(); stoppable_sleep(1, gui_callback)
            _selecionar_ano(driver, wait, ano_alvo, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space()='{mes_final}']"))).click()
            
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aplicar filtros')]"))).click()
            stoppable_sleep(3, gui_callback)

        gui_callback.atualizar_progresso(0, 100, "Filtrando para contar relatórios...")
        aplicar_filtros_completos()
        
        seletor_botoes_consulta = (By.XPATH, "//button[@tooltip='Consultar Lançamentos']")
        numero_de_relatorios = len(driver.find_elements(*seletor_botoes_consulta))
        print(f"Contagem finalizada. Total de {numero_de_relatorios} relatórios.")
        
        gui_callback.atualizar_progresso(0, numero_de_relatorios, f"Encontrados {numero_de_relatorios} relatórios. Iniciando downloads...")

        for i in range(numero_de_relatorios):
            if gui_callback.stop_requested:
                raise InterruptedError("Parada solicitada.")

            print(f"\n--- Iniciando verificação do relatório {i + 1} de {numero_de_relatorios} ---")
            
            try:
                aplicar_filtros_completos()

                botoes_consulta_atualizados = wait.until(EC.presence_of_all_elements_located(seletor_botoes_consulta))
                botoes_consulta_atualizados[i].click()
                
                print("Aguardando carregamento da página do relatório...")
                # --- ALTERAÇÃO 1 AQUI ---
                stoppable_sleep(10, gui_callback) # Reduzido de 30s para 10s

                status_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//h5/span[last()]")))
                status_text = status_element.text.strip().upper()

                if status_text == "APROVADO":
                    print(f"Relatório {i + 1} está APROVADO. Baixando...")
                    stoppable_sleep(20, gui_callback)
                    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., ' Gerar Excel')]"))).click()
                    print("Download iniciado. Aguardando...")
                    # --- ALTERAÇÃO 2 AQUI ---
                    stoppable_sleep(5, gui_callback)
                    gui_callback.atualizar_progresso(i + 1, numero_de_relatorios, f"Baixado {i + 1} de {numero_de_relatorios} relatórios...")
                else:
                    print(f"Relatório {i + 1} com status '{status_element.text}' não será baixado.")
                    gui_callback.atualizar_progresso(i + 1, numero_de_relatorios, f"Relatório {i + 1} '{status_element.text}'. Pulando...")

            except Exception as e_loop:
                print(f"Erro ao processar o relatório {i + 1}: {e_loop}")
                gui_callback.atualizar_progresso(i + 1, numero_de_relatorios, f"Erro no relatório {i + 1}. Pulando...")
                continue
        
        print("\nProcesso de download finalizado.")

    except InterruptedError as e:
        print(f"Processo interrompido pelo usuário: {e}")
        raise e
    except Exception as e_geral:
        print(f"Ocorreu um erro GERAL ao processar o CNPJ {cnpj_alvo}: {e_geral}")
        raise e_geral