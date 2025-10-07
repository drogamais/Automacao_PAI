import os
import re
import pandas as pd
import mariadb
import sys
from datetime import datetime
import numpy as np
from utils.config import DB_CONFIG

# Tabela no banco
TABLE_NAME = "bronze_pai_financeiro"
PASTA_DOS_ARQUIVOS_EXCEL = os.path.join(os.path.dirname(os.path.realpath(__file__)), "downloads")

# --- REGRAS DE EXTRAÇÃO ---
LINHAS_PARA_EXTRAIR = [
    3, 4, 6, 7, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 21, 23, 24, 25, 26, 27, 28,
    29, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 49, 50,
    51, 52, 54, 55, 56, 57, 58, 59
]
LINHAS_POSITIVAS = {3, 59, 60, 61}
COLUNA_INDICADORES = 2  # Corresponde à coluna 'C' (índice 2)

# --- FUNÇÕES AUXILIARES ---
def limpar_valor(valor_str):
    if not valor_str or str(valor_str).strip() == '': return None
    try:
        valor_limpo = str(valor_str).replace('.', '').replace(',', '.')
        return pd.to_numeric(valor_limpo, errors='coerce')
    except (ValueError, TypeError):
        return None

def limpar_percentual(perc_str):
    if perc_str is None or str(perc_str).strip() in ['', '-']:
        return 1.0
    try:
        valor_limpo = str(perc_str).replace(',', '.')
        return float(valor_limpo) / 100
    except (ValueError, TypeError):
        return 1.0

def extrair_dados_do_excel(caminho_arquivo, lojas_map):
    print(f"Lendo arquivo de evolução: {os.path.basename(caminho_arquivo)}...")
    nome_arquivo = os.path.basename(caminho_arquivo)
    
    match = re.search(r'-\s*(\d+)\s*-', nome_arquivo)
    if not match:
        print(f"AVISO: O arquivo de evolução '{nome_arquivo}' não corresponde ao padrão. Pulando...")
        return None

    loja_numero = int(match.group(1))
    loja_nome = lojas_map.get(loja_numero, "NOME NÃO ENCONTRADO")

    df_excel = pd.read_excel(caminho_arquivo, header=None, dtype=str).fillna('')
    dados_extraidos = []
    
    total_linhas_df = df_excel.shape[0]

    for col_idx in range(3, df_excel.shape[1], 2):
        header_value = df_excel.iat[0, col_idx]
        
        if "Média no Período" in str(header_value):
            break
        
        try:
            data_ref = datetime.strptime(f"01/{header_value}", "%d/%m/%Y").date()
        except (ValueError, TypeError):
            print(f"AVISO: Cabeçalho de data inválido '{header_value}' na coluna {col_idx}. Pulando coluna.")
            continue

        for num_linha in LINHAS_PARA_EXTRAIR:
            idx_linha = num_linha - 1
            
            if idx_linha >= total_linhas_df:
                continue

            indicador = df_excel.iat[idx_linha, COLUNA_INDICADORES]
            if not indicador: continue

            valor_geral_raw = df_excel.iat[idx_linha, col_idx]
            percentual_geral_raw = df_excel.iat[idx_linha, col_idx + 1]
            
            valor_numerico = limpar_valor(valor_geral_raw)

            if pd.notna(valor_numerico):
                valor_final = abs(valor_numerico) * (-1 if num_linha not in LINHAS_POSITIVAS else 1)
            else:
                valor_final = None

            dados_linha = {
                "loja_numero": loja_numero, 
                "loja_nome": loja_nome,
                "data_ref": data_ref, 
                "indicador_nome": str(indicador).strip(),
                "valor_geral": valor_final,
                "percentual_geral": limpar_percentual(percentual_geral_raw)
            }
            
            if "Total Líquido de Vendas Realizadas" in dados_linha["indicador_nome"]:
                dados_linha["percentual_geral"] = 1.0

            dados_extraidos.append(dados_linha)
            
    return pd.DataFrame(dados_extraidos).dropna(subset=['valor_geral'])

def main():
    conn = None
    try:
        print("\n--- INICIANDO PROCESSAMENTO DE DADOS DE EVOLUÇÃO FINANCEIRA ---")
        
        print("Carregando lojas...")
        conn = mariadb.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT loja_numero, fantasia FROM bronze_lojas")
        lojas_map = {int(numero): nome for numero, nome in cursor.fetchall() if numero is not None}

        # --- LINHA MODIFICADA ---
        # Agora ignora explicitamente qualquer arquivo que contenha "performance" no nome
        arquivos_excel = [
            f for f in os.listdir(PASTA_DOS_ARQUIVOS_EXCEL) 
            if f.endswith('.xlsx') and 'evolução' in f.lower() and not f.startswith('~$') and 'performance' not in f.lower()
        ]
        
        if not arquivos_excel:
            print(f"Nenhum arquivo de Evolução Financeira (.xlsx) encontrado na pasta: '{PASTA_DOS_ARQUIVOS_EXCEL}'")
            return
        
        todos_os_dados = []
        for arquivo in arquivos_excel:
            caminho_completo = os.path.join(PASTA_DOS_ARQUIVOS_EXCEL, arquivo)
            df_arquivo_atual = extrair_dados_do_excel(caminho_completo, lojas_map)
            if df_arquivo_atual is not None and not df_arquivo_atual.empty:
                todos_os_dados.append(df_arquivo_atual)
    
        if not todos_os_dados:
            print("\nNenhum dado válido de evolução foi extraído. Encerrando.")
        else:
            df_final_completo = pd.concat(todos_os_dados, ignore_index=True)
            df_final_completo = df_final_completo.replace({np.nan: None})

            df_final_completo['valor_media_loja_6m'] = None
            df_final_completo['percentual_media_loja_6m'] = None
            df_final_completo['valor_media_faixa_faturamento_6m'] = None
            df_final_completo['percentual_media_faixa_faturamento_6m'] = None
            df_final_completo['valor_media_febrafar_6m'] = None
            df_final_completo['percentual_media_febrafar_6m'] = None
            
            sql_insert = f"""
                INSERT INTO {TABLE_NAME} (
                    loja_numero, loja_nome, data_ref, indicador_nome, 
                    valor_geral, percentual_geral,
                    valor_media_loja_6m, percentual_media_loja_6m,
                    valor_media_faixa_faturamento_6m, percentual_media_faixa_faturamento_6m,
                    valor_media_febrafar_6m, percentual_media_febrafar_6m
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                    loja_nome=VALUES(loja_nome),
                    valor_geral=VALUES(valor_geral),
                    percentual_geral=VALUES(percentual_geral)
            """
            
            dados_para_inserir = [tuple(row) for row in df_final_completo.to_numpy()]
            
            print(f"\nIniciando inserção/atualização de {len(dados_para_inserir)} registros de evolução...")
            cursor.executemany(sql_insert, dados_para_inserir)
            conn.commit()
            print(f"SUCESSO! {cursor.rowcount} registros de evolução foram inseridos/atualizados na tabela '{TABLE_NAME}'.")

    except mariadb.Error as e:
        print(f"ERRO de banco de dados: {e}")
        if conn: conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()