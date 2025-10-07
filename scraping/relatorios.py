# Arquivo: scraping/relatorios.py
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Imports para a nova lógica de processamento
from processing import financeiro, performance
from utils import system  # <--- LINHA ADICIONADA PARA CORREÇÃO

def stoppable_sleep(duration, gui_callback):
    """Uma função de espera que pode ser interrompida."""
    end_time = time.time() + duration
    while time.time() < end_time:
        if gui_callback.stop_requested:
            raise InterruptedError("Parada solicitada durante a espera.")
        time.sleep(0.1)

def _get_latest_file(path):
    """Encontra o arquivo mais recente em um diretório."""
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if basename.endswith('.xlsx')]
    if not paths:
        return None
    return max(paths, key=os.path.getctime)

def executar_acoes_pai(driver, wait, cnpj_alvo, ano_alvo, mes_inicial, mes_final, gui_callback, lojas_map, conn):
    """
    Executa o download e o processamento sequencial de cada relatório.
    """
    print(f"\nINICIANDO PROCESSAMENTO PARA O CNPJ: {cnpj_alvo} | Período: {mes_inicial}/{ano_alvo} a {mes_final}/{ano_alvo}")
    
    # Define o caminho da pasta de downloads
    project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    pasta_downloads = os.path.join(project_root, "downloads")

    try:
        def aplicar_filtros_completos():
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Avaliação')]"))).click(); stoppable_sleep(2, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Loja')]"))).click(); stoppable_sleep(1, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Selecione...']]"))).click(); stoppable_sleep(1, gui_callback)
            
            input_localizar = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Localizar']")))
            input_localizar.clear()
            input_localizar.send_keys(cnpj_alvo)
            stoppable_sleep(2, gui_callback)

            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'list-item') and contains(text(), '{cnpj_alvo}')]"))).click(); stoppable_sleep(1, gui_callback)
            
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click(); stoppable_sleep(1, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space()='{mes_inicial}']"))).click()
            
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click(); stoppable_sleep(1, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space()='{mes_final}']"))).click()
            
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aplicar filtros')]"))).click()
            stoppable_sleep(3, gui_callback)

        gui_callback.atualizar_progresso(0, 100, "Filtrando para contar relatórios...")
        aplicar_filtros_completos()
        
        seletor_botoes_consulta = (By.XPATH, "//button[@tooltip='Consultar Lançamentos']")
        numero_de_relatorios = len(driver.find_elements(*seletor_botoes_consulta))
        print(f"Contagem finalizada. Total de {numero_de_relatorios} relatórios.")
        
        if numero_de_relatorios == 0:
            gui_callback.atualizar_progresso(100, 100, "Nenhum relatório encontrado para o período.")
            return

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
                stoppable_sleep(10, gui_callback)

                status_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//h5/span[last()]")))
                status_text = status_element.text.strip().upper()

                if status_text == "APROVADO":
                    print(f"Relatório {i + 1} está APROVADO. Baixando...")
                    
                    system.limpar_pasta_downloads()

                    stoppable_sleep(20, gui_callback)
                    wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., ' Gerar Excel')]"))).click()
                    print("Download iniciado. Aguardando conclusão...")
                    
                    time_limit = 30
                    start_time = time.time()
                    latest_file = None
                    while time.time() - start_time < time_limit:
                        latest_file = _get_latest_file(pasta_downloads)
                        if latest_file:
                            break
                        stoppable_sleep(5, gui_callback)
                    
                    if not latest_file:
                        raise Exception("Download do arquivo falhou ou demorou demais.")
                    
                    print(f"Arquivo baixado: {os.path.basename(latest_file)}")
                    gui_callback.atualizar_progresso(i, numero_de_relatorios, f"Baixado {i + 1}/{numero_de_relatorios}. Processando...")

                    if "financeiro" in latest_file.lower():
                        financeiro.processar_arquivo(latest_file, lojas_map, conn)
                    elif "performance" in latest_file.lower():
                        performance.processar_arquivo(latest_file, lojas_map, conn)
                    
                    os.remove(latest_file)
                    print(f"Arquivo {os.path.basename(latest_file)} processado e removido.")

                else:
                    print(f"Relatório {i + 1} com status '{status_element.text}' não será baixado.")
                
                gui_callback.atualizar_progresso(i + 1, numero_de_relatorios, f"Relatório {i + 1}/{numero_de_relatorios} verificado.")
                
                # Volta para a página anterior para selecionar o próximo relatório
                driver.back()
                stoppable_sleep(3, gui_callback)

            except Exception as e_loop:
                print(f"Erro ao processar o relatório {i + 1}: {e_loop}")
                gui_callback.atualizar_progresso(i + 1, numero_de_relatorios, f"Erro no relatório {i + 1}. Pulando...")
                driver.back() 
                stoppable_sleep(3, gui_callback)
                continue
        
        print("\nProcesso de scraping finalizado.")

    except InterruptedError as e:
        print(f"Processo interrompido pelo usuário: {e}")
        raise e
    except Exception as e_geral:
        print(f"Ocorreu um erro GERAL ao processar o CNPJ {cnpj_alvo}: {e_geral}")
        raise e_geral