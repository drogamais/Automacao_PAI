# Arquivo: processing/evolucao_performance.py
import os
import re
import pandas as pd
import mariadb
import sys
from datetime import datetime
import numpy as np
from utils.config import DB_CONFIG

TABLE_NAME = "bronze_pai_performance"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PASTA_DOS_ARQUIVOS_EXCEL = os.path.join(PROJECT_ROOT, "downloads")

LINHAS_PARA_EXTRAIR = [
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44
]
COLUNA_INDICADORES = 1

def limpar_valor(valor_str):
    if valor_str is None or str(valor_str).strip() in ['', '-']: return None
    try:
        valor_limpo = str(valor_str).replace('.', '').replace(',', '.')
        return pd.to_numeric(valor_limpo, errors='coerce')
    except (ValueError, TypeError):
        return None

def extrair_dados_do_excel(caminho_arquivo, lojas_map):
    print(f"Lendo arquivo de evolução de performance: {os.path.basename(caminho_arquivo)}...")
    nome_arquivo = os.path.basename(caminho_arquivo)
    
    match = re.search(r'-\s*(\d+)\s*-', nome_arquivo)
    if not match:
        print(f"AVISO: O arquivo '{nome_arquivo}' não corresponde ao padrão de nome esperado. Pulando...")
        return None

    loja_numero = int(match.group(1))
    loja_nome = lojas_map.get(loja_numero, "NOME NÃO ENCONTRADO")

    df_excel = pd.read_excel(caminho_arquivo, header=None, dtype=str).fillna('')
    dados_extraidos = []
    total_linhas_df = df_excel.shape[0]

    for col_idx in range(2, df_excel.shape[1]):
        header_value = str(df_excel.iat[0, col_idx]).strip()
        
        if "Média no Período" in header_value:
            break
        
        try:
            data_ref = datetime.strptime(f"01/{header_value}", "%d/%m/%Y").date()
        except (ValueError, TypeError):
            continue

        for num_linha in LINHAS_PARA_EXTRAIR:
            idx_linha = num_linha - 1
            
            if idx_linha >= total_linhas_df:
                continue

            indicador = str(df_excel.iat[idx_linha, COLUNA_INDICADORES]).strip()
            if not indicador or indicador.startswith("Performance em relação ao grupo"): continue

            unidade_medida = 'Percentual' if indicador.startswith('%') else 'Decimal'

            valor_raw = df_excel.iat[idx_linha, col_idx]
            valor_limpo = limpar_valor(valor_raw)
            
            metrica_final = None
            if pd.notna(valor_limpo):
                metrica_final = valor_limpo / 100 if unidade_medida == 'Percentual' else valor_limpo

            dados_linha = {
                "loja_numero": loja_numero, 
                "loja_nome": loja_nome,
                "data_ref": data_ref, 
                "indicador_nome": indicador,
                "unidade_medida": unidade_medida,
                "metrica_geral": metrica_final,
            }
            dados_extraidos.append(dados_linha)
            
    if not dados_extraidos:
        return pd.DataFrame()

    return pd.DataFrame(dados_extraidos).dropna(subset=['metrica_geral'])

def main():
    conn = None
    try:
        print("\n--- INICIANDO PROCESSAMENTO DE DADOS DE EVOLUÇÃO DE PERFORMANCE ---")
        conn = mariadb.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Carregando lojas...")
        cursor.execute("SELECT loja_numero, fantasia FROM bronze_lojas")
        lojas_map = {int(numero): nome for numero, nome in cursor.fetchall() if numero is not None}
        print(f"{len(lojas_map)} lojas válidas carregadas com sucesso.")

        arquivos_excel = [
            f for f in os.listdir(PASTA_DOS_ARQUIVOS_EXCEL) 
            if f.endswith('.xlsx') and 'evolução' in f.lower() and 'performance' in f.lower() and not f.startswith('~$')
        ]

        if not arquivos_excel:
            print(f"Nenhum arquivo de Evolução de Performance (.xlsx) encontrado na pasta: '{PASTA_DOS_ARQUIVOS_EXCEL}'")
            return

        todos_os_dados = []
        for arquivo in arquivos_excel:
            caminho_completo = os.path.join(PASTA_DOS_ARQUIVOS_EXCEL, arquivo)
            df_arquivo_atual = extrair_dados_do_excel(caminho_completo, lojas_map)
            if df_arquivo_atual is not None and not df_arquivo_atual.empty:
                todos_os_dados.append(df_arquivo_atual)
        
        if not todos_os_dados:
            print("\nNenhum dado de Performance válido foi extraído dos arquivos.")
        else:
            df_final_completo = pd.concat(todos_os_dados, ignore_index=True)
            df_final_completo = df_final_completo.replace({np.nan: None})

            # Adiciona colunas vazias para manter a compatibilidade
            df_final_completo['metrica_media_loja_6m'] = None
            df_final_completo['metrica_media_faixa_faturamento_6m'] = None
            df_final_completo['metrica_media_febrafar_6m'] = None
            
            sql_insert = f"""
                INSERT INTO {TABLE_NAME} (
                    loja_numero, loja_nome, data_ref, indicador_nome, unidade_medida,
                    metrica_geral, metrica_media_loja_6m, metrica_media_faixa_faturamento_6m, metrica_media_febrafar_6m
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                    loja_nome=VALUES(loja_nome),
                    unidade_medida=VALUES(unidade_medida),
                    metrica_geral=VALUES(metrica_geral)
            """
            
            dados_para_inserir = [tuple(row) for row in df_final_completo.to_numpy()]
            
            # --- LÓGICA DE BATCH APLICADA AQUI ---
            tamanho_lote = 100
            total_registros = len(dados_para_inserir)

            print(f"\nIniciando inserção/atualização de {total_registros} registros de evolução de performance em lotes de {tamanho_lote}...")
            
            registros_processados = 0
            for i in range(0, total_registros, tamanho_lote):
                lote_atual = dados_para_inserir[i:i + tamanho_lote]
                cursor.executemany(sql_insert, lote_atual)
                conn.commit()
                registros_processados += len(lote_atual)
                print(f"  -> Lote de {len(lote_atual)} registros processado. Total: {registros_processados}/{total_registros}")

            print(f"SUCESSO! Operação concluída na tabela '{TABLE_NAME}'.")

    except mariadb.Error as e:
        print(f"ERRO de banco de dados: {e}")
        if conn: conn.rollback()
        # Lança a exceção para que o controller saiba que algo deu errado
        raise e
    finally:
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")
        print("--- PROCESSAMENTO DE EVOLUÇÃO DE PERFORMANCE FINALIZADO ---\n")

if __name__ == "__main__":
    main()