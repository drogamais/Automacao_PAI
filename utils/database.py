# Arquivo: utils/database.py
import mariadb

# --- CONFIGURAÇÕES ---
DB_USER = "drogamais"
DB_PASSWORD = "dB$MYSql@2119"
DB_HOST = "10.48.12.20"
DB_PORT = 3306
DB_NAME = "dbDrogamais"

def buscar_cnpj_no_banco(loja_numero):
    conn = None
    try:
        conn = mariadb.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
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
        conn = mariadb.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
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