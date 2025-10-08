# Arquivo: scraping/login.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Importa a configuração de login diretamente
from utils.config import LOGIN_CONFIG

def stoppable_sleep(duration, gui_callback):
    """Uma função de espera que pode ser interrompida."""
    for i in range(duration):
        if gui_callback.stop_requested:
            raise InterruptedError("Parada solicitada durante a espera.")
        time.sleep(1)

def login_e_navega_para_pai(driver, wait, gui_callback):
    # Usa as credenciais do dicionário importado
    USUARIO = LOGIN_CONFIG['usuario']
    SENHA = LOGIN_CONFIG['senha']
    URL_LOGIN = "https://orion.febrafar.com.br/login"

    gui_callback.atualizar_progresso(33, 100, "Acessando a página da FEBRAFAR...")
    print("Iniciando o navegador e acessando a página de login...")
    driver.get(URL_LOGIN)
    
    if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")

    print("Realizando o login...")
    wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(USUARIO)
    wait.until(EC.visibility_of_element_located((By.ID, "senha"))).send_keys(SENHA)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Entrar')]"))).click()
    wait.until(EC.url_changes(URL_LOGIN))
    
    gui_callback.atualizar_progresso(66, 100, "Login realizado com sucesso!")
    print("\nLogin realizado com sucesso!")

    print("Aguardando o cabeçalho da página (id='header') carregar...")
    wait.until(EC.visibility_of_element_located((By.ID, "header")))
    print("Cabeçalho encontrado.")
    stoppable_sleep(1, gui_callback) 

    if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")

    print("Procurando o botão de menu usando um seletor relacional...")
    seletor_menu = "//button[contains(@title, 'Gabriel')]/parent::div/preceding-sibling::div/button"
    botao_menu = wait.until(EC.element_to_be_clickable((By.XPATH, seletor_menu)))
    ActionChains(driver).move_to_element(botao_menu).click().perform()
    print("Clique no menu realizado com sucesso!")
    stoppable_sleep(1, gui_callback)
    
    print("Aguardando o menu de opções carregar e clicando em 'PAI'...")
    seletor_pai = "//button[.//h3[text()='PAI']]"
    item_pai = wait.until(EC.element_to_be_clickable((By.XPATH, seletor_pai)))
    
    janela_original = driver.current_window_handle
    janelas_antigas = set(driver.window_handles)
    
    item_pai.click()
    
    if gui_callback.stop_requested: raise InterruptedError("Parada solicitada.")
    
    print("Aguardando a nova aba do PAI ser aberta...")
    wait.until(EC.new_window_is_opened(janelas_antigas))
    
    nova_janela_encontrada = None
    for janela in driver.window_handles:
        if janela != janela_original:
            driver.switch_to.window(janela)
            if 'DevTools' not in driver.title:
                nova_janela_encontrada = janela
                break

    if not nova_janela_encontrada:
        driver.switch_to.window(janela_original)
        raise Exception("Não foi possível encontrar a nova aba do aplicativo PAI.")
        
    gui_callback.atualizar_progresso(100, 100, "Página do PAI acessada com sucesso!")
    print(f"Foco do Selenium mudado para a nova aba com título: '{driver.title}'")
    stoppable_sleep(2, gui_callback)
    print("\nNavegação para o PAI realizada com sucesso na nova aba!")
    gui_callback.atualizar_progresso(0, 100, "Primeira Etapa conclúida!")