# Arquivo: utils/webdriver.py
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_driver(debug_mode):
    caminho_script = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), __file__, '..')))
    pasta_downloads = os.path.join(caminho_script, "downloads")
    
    chrome_options = Options()
    prefs = {
        "download.default_directory": pasta_downloads,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "safebrowsing.disable_download_protection": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    chrome_options.add_experimental_option("prefs", prefs)

    if not debug_mode:
        print("Iniciando em modo oculto (headless)...")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
    else:
        print("Iniciando em modo de depuração (navegador visível com DevTools)...")
        chrome_options.add_argument("--auto-open-devtools-for-tabs")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    if debug_mode:
        driver.maximize_window()
        
    return driver