# Arquivo: utils/database.py
import mariadb
from .config import DB_CONFIG # Importa a configuração

def buscar_cnpj_no_banco(loja_numero):
    conn = None
    try:
        # Usa as configurações importadas
        conn = mariadb.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "SELECT cnpj FROM bronze_lojas WHERE loja_numero = ?"
        cursor.execute(query, (loja_numero,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    finally:
        if conn: conn.close()

def buscar_lojas_por_cnpjs(cnpjs):
    """Busca no banco os dados das lojas a partir de uma lista de CNPJs."""
    if not cnpjs:
        return []
    conn = None
    try:
        # Usa as configurações importadas
        conn = mariadb.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        placeholders = ', '.join(['%s'] * len(cnpjs))
        query = f"SELECT loja_numero, cnpj, fantasia FROM bronze_lojas WHERE cnpj IN ({placeholders})"
        cursor.execute(query, tuple(cnpjs))
        return cursor.fetchall()
    except mariadb.Error as e:
        print(f"Erro ao buscar lojas por CNPJ: {e}")
        return []
    finally:
        if conn: conn.close()

        # --- NOVA FUNÇÃO ---
def carregar_mapa_lojas():
    """Carrega o mapa de número da loja para nome fantasia a partir do banco."""
    conn = None
    try:
        conn = mariadb.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT loja_numero, fantasia FROM bronze_lojas")
        lojas_map = {int(numero): nome for numero, nome in cursor.fetchall() if numero is not None}
        return lojas_map
    except mariadb.Error as e:
        print(f"Erro ao carregar mapa de lojas: {e}")
        return {}
    finally:
        if conn:
            conn.close()