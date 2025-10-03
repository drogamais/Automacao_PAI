# Arquivo: step01_login_actions.py

import time
import json 
from sys import exit 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def carregar_credenciais():
    try:
        with open('credenciais.json', 'r') as f:
            credenciais = json.load(f)
            return credenciais['usuario'], credenciais['senha']
    except FileNotFoundError:
        exit("Erro: Arquivo 'credenciais.json' não encontrado!")
    except KeyError:
        exit("Erro: O arquivo 'credenciais.json' deve conter as chaves 'usuario' e 'senha'.")

def login_e_navega_para_pai(driver, wait):
    USUARIO, SENHA = carregar_credenciais()
    URL_LOGIN = "https://orion.febrafar.com.br/login"

    print("Iniciando o navegador e acessando a página de login...")
    driver.get(URL_LOGIN)

    print("Realizando o login...")
    wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(USUARIO)
    wait.until(EC.visibility_of_element_located((By.ID, "senha"))).send_keys(SENHA)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Entrar')]"))).click()
    wait.until(EC.url_changes(URL_LOGIN))
    print("\nLogin realizado com sucesso!")

    # --- PAUSA DE ESTABILIZAÇÃO ADICIONADA ---
    print("Aguardando 3 segundos para o dashboard carregar completamente...")
    time.sleep(3)

    print("Aguardando o cabeçalho da página (id='header') carregar...")
    wait.until(EC.visibility_of_element_located((By.ID, "header")))
    print("Cabeçalho encontrado.")
    time.sleep(1) 

    print("Procurando o botão de menu usando um seletor relacional...")
    seletor_menu = "//button[contains(@title, 'Gabriel')]/parent::div/preceding-sibling::div/button"
    botao_menu = wait.until(EC.element_to_be_clickable((By.XPATH, seletor_menu)))
    ActionChains(driver).move_to_element(botao_menu).click().perform()
    print("Clique no menu realizado com sucesso!")
    time.sleep(1)
    
    print("Aguardando o menu de opções carregar e clicando em 'PAI'...")
    seletor_pai = "//button[.//h3[text()='PAI']]"
    item_pai = wait.until(EC.element_to_be_clickable((By.XPATH, seletor_pai)))
    
    janela_original = driver.current_window_handle
    janelas_antigas = set(driver.window_handles)
    
    item_pai.click()
    
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
        
    print(f"Foco do Selenium mudado para a nova aba com título: '{driver.title}'")
    time.sleep(2)
    print("\nNavegação para o PAI realizada com sucesso na nova aba!")