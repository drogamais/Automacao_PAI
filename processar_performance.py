import os
import re
import pandas as pd
import mariadb
import sys
from datetime import datetime
import numpy as np

# --- CONFIGURAÇÕES ---
DB_USER = "drogamais"
DB_PASSWORD = "dB$MYSql@2119"
DB_HOST = "10.48.12.20"
DB_PORT = 3306
DB_NAME = "dbDrogamais"
TABLE_NAME = "bronze_pai_performance"
PASTA_DOS_ARQUIVOS_EXCEL = r"C:\Users\altaneiro.analista01\Desktop\interface PAI\downloads"

# --- REGRAS DE EXTRAÇÃO PARA PERFORMANCE ---
LINHAS_PARA_EXTRAIR = [
    2, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 20, 22, 24, 26, 28, 30,
    32, 33, 34, 35, 37, 39, 40, 42, 43, 45, 46, 48, 50, 51, 52, 53, 54, 55, 56, 57
]

COLUNA_INDICADORES = 'C'
# <--- NOTA: Estes nomes de colunas referem-se ao Excel, então estão corretos ---
COLUNA_VALOR_LOJA = 'D'
COLUNA_MEDIA_LOJA = 'E'
COLUNA_MEDIA_FAIXA = 'F'
COLUNA_MEDIA_FEBRAFAR = 'G'

# --- FUNÇÃO AUXILIAR ---
def limpar_valor(valor_str):
    """Converte uma string formatada ('1.234,56' ou '82,18') para um número float."""
    if valor_str is None or str(valor_str).strip() == '': return None
    try:
        valor_limpo = str(valor_str).replace('.', '').replace(',', '.')
        return pd.to_numeric(valor_limpo, errors='coerce')
    except (ValueError, TypeError):
        return None

def extrair_dados_do_excel(caminho_arquivo, lojas_map):
    print(f"Lendo arquivo: {os.path.basename(caminho_arquivo)}...")
    nome_arquivo = os.path.basename(caminho_arquivo)
    
    # <--- LINHA CORRIGIDA ---
    match = re.search(r'-\s*(\d+)\s*-.*-\s+(\d+-\d+)\.', nome_arquivo)
    if not match:
        print(f"AVISO: O arquivo '{nome_arquivo}' não corresponde ao padrão de nome esperado. Pulando...")
        return None

    loja_numero = int(match.group(1))
    loja_nome = lojas_map.get(loja_numero, "NOME NÃO ENCONTRADO")
    data_str = match.group(2)

    try:
        data_ref = datetime.strptime(f"01-{data_str}", "%d-%m-%Y").date()
    except ValueError:
        print(f"AVISO: Formato de data inválido '{data_str}'. Pulando...")
        return None

    df_excel = pd.read_excel(caminho_arquivo, header=None, dtype=str).fillna('')
    col_idx_map = {chr(ord('A') + i): i for i in range(26)}
    
    dados_extraidos = []
    for num_linha in LINHAS_PARA_EXTRAIR:
        idx_linha = num_linha - 1
        
        indicador = str(df_excel.iat[idx_linha, col_idx_map[COLUNA_INDICADORES]]).strip()
        if not indicador or indicador.startswith("Performance em relação ao grupo"): continue

        unidade_medida = 'Percentual' if indicador.startswith('%') else 'Decimal'

        def processar_valor(coluna_letra):
            valor_raw = df_excel.iat[idx_linha, col_idx_map[coluna_letra]]
            valor_limpo = limpar_valor(valor_raw)
            if pd.isna(valor_limpo):
                return None
            return valor_limpo / 100 if unidade_medida == 'Percentual' else valor_limpo

        dados_linha = {
            "loja_numero": loja_numero, 
            "loja_nome": loja_nome,
            "data_ref": data_ref, 
            "indicador_nome": indicador,
            "unidade_medida": unidade_medida,
            "metrica_geral": processar_valor(COLUNA_VALOR_LOJA),
            "metrica_media_loja_6m": processar_valor(COLUNA_MEDIA_LOJA),
            "metrica_media_faixa_faturamento_6m": processar_valor(COLUNA_MEDIA_FAIXA),
            "metrica_media_febrafar_6m": processar_valor(COLUNA_MEDIA_FEBRAFAR),
        }
        dados_extraidos.append(dados_linha)
        
    if not dados_extraidos:
        return pd.DataFrame()

    return pd.DataFrame(dados_extraidos).dropna(subset=['metrica_geral'])

def main():
    conn = None
    try:
        print("\n--- INICIANDO PROCESSAMENTO DE DADOS DE PERFORMANCE ---")
        conn = mariadb.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
        cursor = conn.cursor()

        print("Carregando lojas...")
        cursor.execute("SELECT loja_numero, fantasia FROM bronze_lojas")
        lojas_map = {int(numero): nome for numero, nome in cursor.fetchall() if numero is not None}
        print(f"{len(lojas_map)} lojas válidas carregadas com sucesso.")

        todos_os_dados = []
        arquivos_excel = [f for f in os.listdir(PASTA_DOS_ARQUIVOS_EXCEL) if f.endswith('.xlsx') and "performance" in f.lower() and not f.startswith('~$')]
        if not arquivos_excel:
            print(f"Nenhum arquivo Excel (.xlsx) encontrado na pasta: '{PASTA_DOS_ARQUIVOS_EXCEL}'")
        else:
            for arquivo in arquivos_excel:
                # Ignora qualquer arquivo que contenha "financeiro" no nome
                if "financeiro" in arquivo.lower():
                    print(f"INFO: Ignorando arquivo de Financeiro: {arquivo}")
                    continue
                

                caminho_completo = os.path.join(PASTA_DOS_ARQUIVOS_EXCEL, arquivo)
                df_arquivo_atual = extrair_dados_do_excel(caminho_completo, lojas_map)
                if df_arquivo_atual is not None and not df_arquivo_atual.empty:
                    todos_os_dados.append(df_arquivo_atual)
        
        if not todos_os_dados:
            print("\nNenhum dado de Performance válido foi extraído dos arquivos.")
        else:
            df_final_completo = pd.concat(todos_os_dados, ignore_index=True)
            
            ordem_colunas_db = [
                'loja_numero', 'loja_nome', 'data_ref', 'indicador_nome', 
                'unidade_medida', 'metrica_geral', 'metrica_media_loja_6m', 
                'metrica_media_faixa_faturamento_6m', 'metrica_media_febrafar_6m'
            ]
            df_final_completo = df_final_completo[ordem_colunas_db]
            df_final_completo = df_final_completo.replace({np.nan: None})

            sql_insert = f"""
                INSERT INTO {TABLE_NAME} (
                    loja_numero, loja_nome, data_ref, indicador_nome, unidade_medida,
                    metrica_geral, metrica_media_loja_6m, metrica_media_faixa_faturamento_6m, metrica_media_febrafar_6m
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                    loja_nome=VALUES(loja_nome),
                    unidade_medida=VALUES(unidade_medida),
                    metrica_geral=VALUES(metrica_geral),
                    metrica_media_loja_6m=VALUES(metrica_media_loja_6m),
                    metrica_media_faixa_faturamento_6m=VALUES(metrica_media_faixa_faturamento_6m),
                    metrica_media_febrafar_6m=VALUES(metrica_media_febrafar_6m)
            """
            
            dados_para_inserir = [tuple(row) for row in df_final_completo.to_numpy()]
            tamanho_lote = 100
            total_registros = len(dados_para_inserir)

            print(f"\nIniciando inserção/atualização de {total_registros} registros de Performance em lotes de {tamanho_lote}...")

            # O try/except foi removido daqui para simplificar conforme o código base que você enviou
            for i in range(0, total_registros, tamanho_lote):
                lote_atual = dados_para_inserir[i:i + tamanho_lote]
                cursor.executemany(sql_insert, lote_atual)
                conn.commit()
                print(f"  -> Lote de {len(lote_atual)} registros processado.")

            print(f"SUCESSO! Operação de Performance concluída na tabela '{TABLE_NAME}'.")

    except mariadb.Error as e:
        print(f"ERRO: {e}")
        if conn and conn.open: conn.rollback()
        # sys.exit(1) # Removido para não parar o fluxo principal (run.py)
    finally:
        if conn and conn.open:
            conn.close()
            print("Conexão com o banco de dados fechada.")
        print("--- PROCESSAMENTO DE PERFORMANCE FINALIZADO ---\n")


if __name__ == "__main__":
    main()