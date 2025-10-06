# Arquivo: step02_pai_actions.py

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

def executar_acoes_pai(driver, wait, cnpj_alvo, gui_callback):
    """
    Executa o processo de download, verifica a flag de parada a cada iteração
    e envia atualizações de progresso para a GUI.
    """
    print(f"\nINICIANDO PROCESSAMENTO PARA O CNPJ: {cnpj_alvo}")
    
    try:
        # VERIFICAÇÃO DE PARADA ANTES DE COMEÇAR
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada antes da contagem.")
        
        gui_callback.atualizar_progresso(0, 100, "Filtrando para contar relatórios...")
        seletor_avaliacao_inicial = (By.XPATH, "//a[contains(., 'Avaliação')]")
        wait.until(EC.element_to_be_clickable(seletor_avaliacao_inicial)).click()
        stoppable_sleep(2, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Loja')]"))).click(); stoppable_sleep(1, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Selecione...']]"))).click(); stoppable_sleep(1, gui_callback)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Localizar']"))).send_keys(cnpj_alvo); stoppable_sleep(2, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'list-item') and contains(text(), '{cnpj_alvo}')]"))).click(); stoppable_sleep(1, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click(); stoppable_sleep(1, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Jan']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click(); stoppable_sleep(1, gui_callback)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Dez']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aplicar filtros')]"))).click()
        stoppable_sleep(3, gui_callback)
        
        seletor_botoes_consulta = (By.XPATH, "//button[@tooltip='Consultar Lançamentos']")
        numero_de_relatorios = len(driver.find_elements(*seletor_botoes_consulta))
        print(f"Contagem finalizada. Total de {numero_de_relatorios} relatórios.")
        
        gui_callback.atualizar_progresso(0, numero_de_relatorios, f"Encontrados {numero_de_relatorios} relatórios. Iniciando downloads...")

        for i in range(numero_de_relatorios):
            if gui_callback.stop_requested:
                raise InterruptedError("Parada solicitada durante o loop de downloads.")

            print(f"\n--- Iniciando verificação do relatório {i + 1} de {numero_de_relatorios} ---")
            
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Avaliação')]"))).click(); stoppable_sleep(2, gui_callback)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Loja')]"))).click(); stoppable_sleep(1, gui_callback)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Selecione...']]"))).click(); stoppable_sleep(1, gui_callback)
                wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Localizar']"))).send_keys(cnpj_alvo); stoppable_sleep(2, gui_callback)
                wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'list-item') and contains(text(), '{cnpj_alvo}')]"))).click(); stoppable_sleep(1, gui_callback)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click(); stoppable_sleep(1, gui_callback)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Jan']"))).click()
                wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click(); stoppable_sleep(1, gui_callback)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Dez']"))).click()
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aplicar filtros')]"))).click(); stoppable_sleep(3, gui_callback)

                botoes_consulta_atualizados = wait.until(EC.presence_of_all_elements_located(seletor_botoes_consulta))
                botoes_consulta_atualizados[i].click()
                
                print("Aguardando carregamento da página do relatório...")
                stoppable_sleep(30, gui_callback)

                status_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//h5/span[last()]")))
                status_text = status_element.text.strip().upper()

                if status_text == "APROVADO":
                    print(f"Relatório {i + 1} está APROVADO. Baixando...")
                    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., ' Gerar Excel')]"))).click()
                    print("Download iniciado. Aguardando...")
                    stoppable_sleep(10, gui_callback)
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