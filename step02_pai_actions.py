# Arquivo: step02_pai_actions.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
        # ... (código para aplicar filtros e contar relatórios - sem alterações)
        seletor_avaliacao_inicial = (By.XPATH, "//a[contains(., 'Avaliação')]")
        wait.until(EC.element_to_be_clickable(seletor_avaliacao_inicial)).click()
        time.sleep(2)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Loja')]"))).click(); time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Selecione...']]"))).click(); time.sleep(1)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Localizar']"))).send_keys(cnpj_alvo); time.sleep(2)
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'list-item') and contains(text(), '{cnpj_alvo}')]"))).click(); time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click(); time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Jan']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click(); time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Dez']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aplicar filtros')]"))).click()
        time.sleep(3)
        
        seletor_botoes_consulta = (By.XPATH, "//button[@tooltip='Consultar Lançamentos']")
        numero_de_relatorios = len(driver.find_elements(*seletor_botoes_consulta))
        print(f"Contagem finalizada. Total de {numero_de_relatorios} relatórios.")
        
        gui_callback.atualizar_progresso(0, numero_de_relatorios, f"Encontrados {numero_de_relatorios} relatórios. Iniciando downloads...")

        for i in range(numero_de_relatorios):
            # --- VERIFICAÇÃO DE PARADA A CADA LOOP ---
            if gui_callback.stop_requested:
                raise InterruptedError("Parada solicitada durante o loop de downloads.")

            print(f"\n--- Iniciando download do relatório {i + 1} de {numero_de_relatorios} ---")
            
            try:
                # ... (código para reaplicar filtros, clicar e baixar - sem alterações)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Avaliação')]"))).click(); time.sleep(2)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Loja')]"))).click(); time.sleep(1)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Selecione...']]"))).click(); time.sleep(1)
                wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Localizar']"))).send_keys(cnpj_alvo); time.sleep(2)
                wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'list-item') and contains(text(), '{cnpj_alvo}')]"))).click(); time.sleep(1)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click(); time.sleep(1)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Jan']"))).click()
                wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click(); time.sleep(1)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//li[normalize-space()='Dez']"))).click()
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aplicar filtros')]"))).click(); time.sleep(3)

                botoes_consulta_atualizados = wait.until(EC.presence_of_all_elements_located(seletor_botoes_consulta))
                botoes_consulta_atualizados[i].click()
                time.sleep(30)

                wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., ' Gerar Excel')]"))).click()
                print("Download iniciado. Aguardando...")
                time.sleep(10)
                
                gui_callback.atualizar_progresso(i + 1, numero_de_relatorios, f"Baixado {i + 1} de {numero_de_relatorios} relatórios...")

            except Exception as e_loop:
                print(f"Erro no download do relatório {i + 1}: {e_loop}")
                continue
        
        print("\nProcesso de download finalizado.")

    except InterruptedError as e:
        print(f"Processo interrompido pelo usuário: {e}")
        # Não faz nada, só deixa a exceção subir para o run.py
        raise e
    except Exception as e_geral:
        print(f"Ocorreu um erro GERAL ao processar o CNPJ {cnpj_alvo}: {e_geral}")
        raise e_geral