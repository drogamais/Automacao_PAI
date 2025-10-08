# Arquivo: controller/automation.py
from selenium.webdriver.support.ui import WebDriverWait

from scraping import login, relatorios, evolucao, busca
from processing import evolucao_financeiro, evolucao_performance

from utils import database, system, webdriver

def executar_workflow_completo(loja_numero, ano_inicial, mes_inicial, ano_final, mes_final, gui_callback, debug_mode):
    driver = None
    try:
        system.limpar_pasta_downloads()
        gui_callback.atualizar_progresso(0, 100, f"Buscando CNPJ para a loja {loja_numero}...")
        
        lojas_map = database.carregar_mapa_lojas()
        
        cnpj_selecionado = database.buscar_cnpj_no_banco(loja_numero)
        if not cnpj_selecionado:
            raise ValueError(f"Loja {loja_numero} não encontrada no banco de dados.")

        gui_callback.atualizar_progresso(0, 100, f"CNPJ {cnpj_selecionado} encontrado. Iniciando navegador...")
        driver = webdriver.setup_driver(debug_mode)
        wait = WebDriverWait(driver, 60)
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(0, 100, "Realizando login...")
        login.login_e_navega_para_pai(driver, wait, gui_callback)
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        relatorios.executar_acoes_pai(driver, wait, cnpj_selecionado, ano_inicial, mes_inicial, ano_final, mes_final, gui_callback, lojas_map)
        
    except Exception as e:
        raise e
    finally:
        if driver:
            driver.quit()

def executar_workflow_evolucao(loja_numero, ano_inicial, mes_inicial, ano_final, mes_final, gui_callback, debug_mode):
    driver = None
    try:
        system.fechar_processos_excel()
        system.limpar_pasta_downloads()
        
        cnpj_selecionado = database.buscar_cnpj_no_banco(loja_numero)
        if not cnpj_selecionado:
            raise ValueError(f"Loja {loja_numero} não encontrada.")

        driver = webdriver.setup_driver(debug_mode)
        wait = WebDriverWait(driver, 60)
        
        login.login_e_navega_para_pai(driver, wait, gui_callback)
        evolucao.executar_evolution_actions(driver, wait, cnpj_selecionado, ano_inicial, mes_inicial, ano_final, mes_final, gui_callback)
        
        if driver: driver.quit()

        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(0, 100, "Processando Evolução Financeira...")
        evolucao_financeiro.main()

        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(50, 100, "Processando Evolução de Performance...")
        evolucao_performance.main()
        
        gui_callback.atualizar_progresso(100, 100, "Dados inseridos no banco com sucesso!")

    finally:
        if driver:
            driver.quit()

def executar_workflow_busca(ano_alvo, gui_callback, results_callback, debug_mode):
    driver = None
    try:
        gui_callback.atualizar_progresso(0, 100, "Verificando conexão...", is_search=True)
        if not system.check_internet_connection():
            raise ConnectionError("Sem conexão com a internet.")

        gui_callback.atualizar_progresso(5, 100, "Iniciando navegador...", is_search=True)
        driver = webdriver.setup_driver(debug_mode)
        wait = WebDriverWait(driver, 60)
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(10, 100, "Realizando login...", is_search=True)
        login.login_e_navega_para_pai(driver, wait, gui_callback)
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        lojas_encontradas = busca.executar_busca_lojas(driver, wait, ano_alvo, gui_callback)
        
        if lojas_encontradas:
            cnpjs_apenas = [loja['cnpj'] for loja in lojas_encontradas]
            gui_callback.atualizar_progresso(90, 100, "Buscando dados das lojas no banco...", is_search=True)
            lojas_info_db = database.buscar_lojas_por_cnpjs(cnpjs_apenas)
            
            db_info_map = {loja['cnpj']: loja for loja in lojas_info_db}
            lojas_info_final = []
            for loja_encontrada in lojas_encontradas:
                cnpj = loja_encontrada['cnpj']
                if cnpj in db_info_map:
                    loja_info_completa = {**db_info_map[cnpj], **loja_encontrada}
                    lojas_info_final.append(loja_info_completa)
            
            results_callback(lojas_info_final)
        else:
            results_callback([])
            
    finally:
        if driver:
            driver.quit()

def executar_workflow_em_lote(lojas_selecionadas, ano_inicial, mes_inicial, ano_final, mes_final, gui_callback, debug_mode):
    total_lojas = len(lojas_selecionadas)
    gui_callback.atualizar_progresso(0, total_lojas, f"Iniciando automação em lote para {total_lojas} lojas.")
    
    driver = None
    try:
        gui_callback.atualizar_progresso(0, total_lojas, "Iniciando navegador e fazendo login (uma vez)...")
        driver = webdriver.setup_driver(debug_mode)
        wait = WebDriverWait(driver, 60)
        login.login_e_navega_para_pai(driver, wait, gui_callback)

        lojas_map = database.carregar_mapa_lojas() 

        for i, (chk_widget, loja_info) in enumerate(lojas_selecionadas):
            if gui_callback.stop_requested:
                raise InterruptedError("Processo em lote interrompido.")

            loja_numero = loja_info['loja_numero']
            cnpj = loja_info['cnpj']
            
            gui_callback.atualizar_progresso(i, total_lojas, f"Processando {i+1}/{total_lojas}: {loja_numero}")
            
            try:
                relatorios.executar_acoes_pai(driver, wait, cnpj, ano_inicial, mes_inicial, ano_final, mes_final, gui_callback, lojas_map)
                gui_callback.marcar_loja_como_concluida(chk_widget)
            except Exception as e:
                print(f"Erro ao processar a loja {loja_numero}: {e}. Continuando para a próxima...")
                continue
            
    except InterruptedError as e:
        gui_callback.finalizar_automacao(sucesso=False, mensagem=str(e))
    except Exception as e:
        print(f"Erro fatal no workflow em lote: {e}")
        raise e
    finally:
        if driver:
            driver.quit()

    if not gui_callback.stop_requested:
        gui_callback.atualizar_progresso(total_lojas, total_lojas, "Automação em lote finalizada.")