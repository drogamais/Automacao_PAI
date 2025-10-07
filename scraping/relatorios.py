# Arquivo: scraping/relatorios.py
import os
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Imports para a nova lógica de processamento
from processing import financeiro, performance
from utils import system

def stoppable_sleep(duration, gui_callback):
    """Uma função de espera que pode ser interrompida."""
    end_time = time.time() + duration
    while time.time() < end_time:
        if gui_callback.stop_requested:
            raise InterruptedError("Parada solicitada durante a espera.")
        time.sleep(0.1)

def _get_downloaded_files(path):
    """Encontra todos os arquivos .xlsx em um diretório."""
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if basename.endswith('.xlsx') and not basename.startswith('~$')]
    return paths

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

def executar_acoes_pai(driver, wait, cnpj_alvo, ano_alvo, mes_inicial, mes_final, gui_callback, lojas_map, conn):
    """
    Executa o download e o processamento de todos os relatórios, navegando pela paginação.
    """
    print(f"\nINICIANDO PROCESSAMENTO PARA O CNPJ: {cnpj_alvo} | Período: {mes_inicial}/{ano_alvo} a {mes_final}/{ano_alvo}")
    
    project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    pasta_downloads = os.path.join(project_root, "downloads")

    try:
        def aplicar_filtros_e_contar():
            driver.get("https://pai.febrafar.com.br/#!/avaliacao")
            stoppable_sleep(3, gui_callback)

            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Avaliação')]"))).click(); stoppable_sleep(2, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Loja')]"))).click(); stoppable_sleep(1, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Selecione...']]"))).click(); stoppable_sleep(1, gui_callback)
            
            input_localizar = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Localizar']")))
            input_localizar.clear()
            input_localizar.send_keys(cnpj_alvo)
            stoppable_sleep(2, gui_callback)

            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'list-item') and contains(text(), '{cnpj_alvo}')]"))).click(); stoppable_sleep(1, gui_callback)
            
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período inicial...']]"))).click(); stoppable_sleep(1, gui_callback)
            _selecionar_ano(driver, wait, ano_alvo, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space()='{mes_inicial}']"))).click()
            
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'combobox') and .//span[text()='Período final...']]"))).click(); stoppable_sleep(1, gui_callback)
            _selecionar_ano(driver, wait, ano_alvo, gui_callback)
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[normalize-space()='{mes_final}']"))).click()
            
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aplicar filtros')]"))).click()
            stoppable_sleep(5, gui_callback)

            # --- NOVA LÓGICA DE CONTAGEM ---
            try:
                info_element = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'info mr-3 my-1')]/span")))
                info_text = info_element.text
                # Extrai o último número do texto "Exibindo registros de 1 até 10 de 11 registros encontrados."
                match = re.search(r'de (\d+) registros encontrados', info_text)
                if match:
                    return int(match.group(1))
                else:
                    # Se o padrão não corresponder, conta os elementos na página como um fallback
                    return len(driver.find_elements(By.XPATH, "//button[@tooltip='Consultar Lançamentos']"))
            except (TimeoutException, NoSuchElementException):
                print("Nenhum registro encontrado.")
                return 0

        numero_de_relatorios = aplicar_filtros_e_contar()
        print(f"Contagem finalizada. Total de {numero_de_relatorios} relatórios para o período.")
        
        if numero_de_relatorios == 0:
            gui_callback.atualizar_progresso(100, 100, "Nenhum relatório encontrado para o período.")
            return

        gui_callback.atualizar_progresso(0, numero_de_relatorios, f"Encontrados {numero_de_relatorios} relatórios. Iniciando downloads...")
        
        pagina_atual = -1

        for i in range(numero_de_relatorios):
            if gui_callback.stop_requested:
                raise InterruptedError("Parada solicitada.")

            print(f"\n--- Iniciando verificação do relatório {i + 1} de {numero_de_relatorios} ---")
            
            try:
                pagina_alvo = i // 10
                
                # Se o relatório não está na página atual, navega para a página correta
                if pagina_alvo != pagina_atual:
                    print(f"Relatório {i + 1} está na página {pagina_alvo + 1}. Navegando...")
                    aplicar_filtros_e_contar() # Volta para a primeira página
                    for page_click in range(pagina_alvo):
                        seletor_proximo = (By.XPATH, "//li[contains(@class, 'pagination-next') and not(contains(@class, 'disabled'))]/a")
                        botao_proximo = wait.until(EC.element_to_be_clickable(seletor_proximo))
                        botao_proximo.click()
                        stoppable_sleep(3, gui_callback)
                    pagina_atual = pagina_alvo

                index_na_pagina = i % 10
                seletor_botoes_consulta = (By.XPATH, "//button[@tooltip='Consultar Lançamentos']")
                botoes_consulta_atualizados = wait.until(EC.presence_of_all_elements_located(seletor_botoes_consulta))
                
                if index_na_pagina >= len(botoes_consulta_atualizados):
                    raise IndexError(f"Erro de índice: Tentando acessar o relatório {index_na_pagina + 1} na página, mas apenas {len(botoes_consulta_atualizados)} foram encontrados.")

                botoes_consulta_atualizados[index_na_pagina].click()
                
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
                    
                    time_limit = 45
                    start_time = time.time()
                    downloaded_files = []
                    while time.time() - start_time < time_limit:
                        downloaded_files = _get_downloaded_files(pasta_downloads)
                        if downloaded_files:
                            stoppable_sleep(5, gui_callback)
                            downloaded_files = _get_downloaded_files(pasta_downloads)
                            break
                        stoppable_sleep(5, gui_callback)
                    
                    if not downloaded_files:
                        raise Exception("Download do(s) arquivo(s) falhou ou demorou demais.")
                    
                    gui_callback.atualizar_progresso(i, numero_de_relatorios, f"Baixado(s) {len(downloaded_files)} arquivo(s). Processando...")

                    for file_path in downloaded_files:
                        print(f"Processando arquivo: {os.path.basename(file_path)}")
                        if "financeiro" in file_path.lower():
                            financeiro.processar_arquivo(file_path, lojas_map, conn)
                        elif "performance" in file_path.lower():
                            performance.processar_arquivo(file_path, lojas_map, conn)
                        
                        os.remove(file_path)
                        print(f"Arquivo {os.path.basename(file_path)} processado e removido.")
                else:
                    print(f"Relatório {i + 1} com status '{status_element.text}' não será baixado.")
                
                gui_callback.atualizar_progresso(i + 1, numero_de_relatorios, f"Relatório {i + 1}/{numero_de_relatorios} verificado.")
                
                # Após processar um item, é preciso voltar para a lista para o próximo
                driver.back()
                stoppable_sleep(3, gui_callback)
                
            except Exception as e_loop:
                print(f"Erro ao processar o relatório {i + 1}: {e_loop}")
                gui_callback.atualizar_progresso(i + 1, numero_de_relatorios, f"Erro no relatório {i + 1}. Pulando...")
                # Força o retorno para a página de avaliação para tentar o próximo
                driver.get("https://pai.febrafar.com.br/#!/avaliacao")
                pagina_atual = -1 # Reseta o contador da página
                continue
        
        print("\nProcesso de scraping finalizado.")

    except InterruptedError as e:
        print(f"Processo interrompido pelo usuário: {e}")
        raise e
    except Exception as e_geral:
        print(f"Ocorreu um erro GERAL ao processar o CNPJ {cnpj_alvo}: {e_geral}")
        raise e_geral