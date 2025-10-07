# Arquivo: controller/automation.py
import mariadb
import sys
from selenium.webdriver.support.ui import WebDriverWait

# Importa as tarefas de scraping e processamento
from scraping import login, relatorios, evolucao, busca
from processing import evolucao_financeiro, evolucao_performance

# Importa os utilitários
from utils import database, system, webdriver
from utils.config import DB_CONFIG

# --- WORKFLOWS ---

# A função executar_workflow_completo permanece a mesma para a execução de UMA ÚNICA loja.
def executar_workflow_completo(loja_numero, ano_alvo, mes_inicial, mes_final, gui_callback, debug_mode):
    driver = None
    conn = None
    try:
        system.limpar_pasta_downloads()
        gui_callback.atualizar_progresso(0, 100, f"Buscando CNPJ para a loja {loja_numero}...")
        
        print("Conectando ao banco de dados...")
        conn = mariadb.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Carregando lojas...")
        cursor.execute("SELECT loja_numero, fantasia FROM bronze_lojas")
        lojas_map = {int(numero): nome for numero, nome in cursor.fetchall() if numero is not None}

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
        relatorios.executar_acoes_pai(driver, wait, cnpj_selecionado, ano_alvo, mes_inicial, mes_final, gui_callback, lojas_map, conn)
        
    except Exception as e:
        raise e
    finally:
        if driver:
            driver.quit()
        if conn and conn.open:
            conn.close()
            print("Conexão com o banco de dados fechada.")

# A função executar_workflow_evolucao também foi ajustada para seguir a mesma lógica
def executar_workflow_evolucao(loja_numero, ano_alvo, mes_inicial, mes_final, gui_callback, debug_mode):
    driver = None
    conn = None
    try:
        gui_callback.atualizar_progresso(0, 100, "Verificando conexão com a internet...")
        if not system.check_internet_connection():
            raise ConnectionError("Sem conexão com a internet.")
            
        system.fechar_processos_excel()
        system.limpar_pasta_downloads()

        print("Conectando ao banco de dados...")
        conn = mariadb.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Carregando lojas...")
        cursor.execute("SELECT loja_numero, fantasia FROM bronze_lojas")
        lojas_map = {int(numero): nome for numero, nome in cursor.fetchall() if numero is not None}

        gui_callback.atualizar_progresso(0, 100, f"Buscando CNPJ para a loja {loja_numero}...")
        cnpj_selecionado = database.buscar_cnpj_no_banco(loja_numero)
        if not cnpj_selecionado:
            raise ValueError(f"Loja {loja_numero} não encontrada.")

        gui_callback.atualizar_progresso(0, 100, f"CNPJ {cnpj_selecionado} encontrado. Iniciando navegador...")
        driver = webdriver.setup_driver(debug_mode)
        wait = WebDriverWait(driver, 60)
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        gui_callback.atualizar_progresso(0, 100, "Realizando login...")
        login.login_e_navega_para_pai(driver, wait, gui_callback)
        
        if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
        # Chamada única para a nova função de scraping e processamento
        evolucao.executar_evolution_actions(driver, wait, cnpj_selecionado, ano_alvo, mes_inicial, mes_final, gui_callback, lojas_map, conn)
        
    except Exception as e:
        raise e
    finally:
        if driver:
            driver.quit()
        if conn and conn.open:
            conn.close()
            print("Conexão com o banco de dados fechada.")


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

# --- FUNÇÃO MODIFICADA PARA EXECUÇÃO EM LOTE OTIMIZADA ---
def executar_workflow_em_lote(lojas_selecionadas, ano_alvo, mes_inicial, mes_final, gui_callback, debug_mode):
    total_lojas = len(lojas_selecionadas)
    gui_callback.atualizar_progresso(0, total_lojas, f"Iniciando automação em lote para {total_lojas} lojas.")
    
    driver = None
    conn = None
    try:
        # --- ETAPA 1: SETUP INICIAL (FORA DO LOOP) ---
        system.limpar_pasta_downloads()
        
        gui_callback.atualizar_progresso(0, total_lojas, "Conectando ao banco de dados...")
        conn = mariadb.connect(**DB_CONFIG)
        cursor = conn.cursor()

        gui_callback.atualizar_progresso(0, total_lojas, "Carregando mapa de lojas...")
        cursor.execute("SELECT loja_numero, fantasia FROM bronze_lojas")
        lojas_map = {int(numero): nome for numero, nome in cursor.fetchall() if numero is not None}

        gui_callback.atualizar_progresso(0, total_lojas, "Iniciando navegador e fazendo login (uma vez)...")
        driver = webdriver.setup_driver(debug_mode)
        wait = WebDriverWait(driver, 60)
        login.login_e_navega_para_pai(driver, wait, gui_callback)

        # --- ETAPA 2: LOOP PELAS LOJAS (REUTILIZANDO NAVEGADOR E CONEXÃO) ---
        for i, (chk_widget, loja_info) in enumerate(lojas_selecionadas):
            if gui_callback.stop_requested:
                raise InterruptedError("Processo em lote interrompido.")

            loja_numero = loja_info['loja_numero']
            cnpj = loja_info['cnpj']
            
            gui_callback.atualizar_progresso(i, total_lojas, f"Processando {i+1}/{total_lojas}: {loja_numero} - {loja_info['fantasia']}")
            
            try:
                # Chama diretamente a função de scraping, que já está preparada para isso
                relatorios.executar_acoes_pai(driver, wait, cnpj, ano_alvo, mes_inicial, mes_final, gui_callback, lojas_map, conn)
                gui_callback.marcar_loja_como_concluida(chk_widget)
            except Exception as e:
                print(f"Erro ao processar a loja {loja_numero}: {e}. Continuando para a próxima...")
                # A automação continuará para a próxima loja mesmo se uma falhar
                continue
            
    except InterruptedError as e:
        gui_callback.finalizar_automacao(sucesso=False, mensagem=str(e))
    except Exception as e:
        print(f"Erro fatal no workflow em lote: {e}")
        # Relança a exceção para ser capturada pelo wrapper principal
        raise e
    finally:
        # --- ETAPA 3: FINALIZAÇÃO (FORA DO LOOP) ---
        if driver:
            driver.quit()
        if conn and conn.open:
            conn.close()
            print("Conexão com o banco de dados fechada.")

    if not gui_callback.stop_requested:
        gui_callback.atualizar_progresso(total_lojas, total_lojas, "Automação em lote finalizada.")