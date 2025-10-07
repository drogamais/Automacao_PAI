import os
import re
import pandas as pd
import mariadb
import sys
from datetime import datetime
import numpy as np
from utils.config import DB_CONFIG

# Tabela usada no banco
TABLE_NAME = "bronze_pai_financeiro"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PASTA_DOS_ARQUIVOS_EXCEL = os.path.join(PROJECT_ROOT, "downloads")

# --- REGRAS DE EXTRAÇÃO ---
LINHAS_PARA_EXTRAIR = [
    3, 8, 9, 12, 13, 14, 15, 18, 19, 20, 21, 22, 23, 26, 29, 30, 31, 32, 33, 34, 35, 
    38, 39, 40, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 55, 56, 59, 60, 61, 
    66, 67, 68, 69, 70, 71
]
LINHAS_POSITIVAS = {3, 59, 60, 61}
COLUNA_INDICADORES = 'C'
COLUNA_VALOR_GERAL = 'D'
COLUNA_PERCENTUAL_GERAL = 'E'
COLUNA_VALOR_MEDIA_LOJA = 'F'
COLUNA_PERCENTUAL_MEDIA_LOJA = 'G'
COLUNA_VALOR_MEDIA_FAIXA = 'H'
COLUNA_PERCENTUAL_MEDIA_FAIXA = 'I'
COLUNA_VALOR_MEDIA_FEBRAFAR = 'J'
COLUNA_PERCENTUAL_MEDIA_FEBRAFAR = 'K'

# --- FUNÇÕES AUXILIARES ---
def limpar_valor(valor_str):
    """Converte uma string formatada ('1.234,56') para um número float."""
    if not valor_str or str(valor_str).strip() == '': return None
    try:
        valor_limpo = str(valor_str).replace('.', '').replace(',', '.')
        return pd.to_numeric(valor_limpo, errors='coerce')
    except (ValueError, TypeError):
        return None

# <--- FUNÇÃO ALTERADA ---
def limpar_percentual(perc_str):
    """
    Converte uma string de percentual ('32,93') para um float decimal (0.3293).
    Se o valor for NULO, vazio ou '-', retorna 1.0 (100%).
    """
    # Verifica as condições para retornar 1.0 (100%)
    # str(perc_str).strip() lida com células vazias ou com espaços em branco
    if perc_str is None or str(perc_str).strip() in ['', '-']:
        return 1.0

    # Se não for uma das condições acima, tenta a conversão normal
    try:
        valor_limpo = str(perc_str).replace(',', '.')
        return float(valor_limpo) / 100
    except (ValueError, TypeError):
        # Se a conversão falhar (ex: um texto inesperado), também retorna 1.0 como um valor padrão seguro
        return 1.0

def extrair_dados_do_excel(caminho_arquivo, lojas_map):
    print(f"Lendo arquivo: {os.path.basename(caminho_arquivo)}...")
    nome_arquivo = os.path.basename(caminho_arquivo)
    match = re.search(r'-\s*(\d+)\s*-.*-\s+(\d+-\d+)\.', nome_arquivo)
    
    if not match:
        print(f"AVISO: O arquivo '{nome_arquivo}' não corresponde ao padrão. Pulando...")
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
        
        indicador = df_excel.iat[idx_linha, col_idx_map[COLUNA_INDICADORES]]
        if not indicador: continue

        valor_geral_raw = df_excel.iat[idx_linha, col_idx_map[COLUNA_VALOR_GERAL]]
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
            "percentual_geral": limpar_percentual(df_excel.iat[idx_linha, col_idx_map[COLUNA_PERCENTUAL_GERAL]]),
            "valor_media_loja_6m": limpar_valor(df_excel.iat[idx_linha, col_idx_map[COLUNA_VALOR_MEDIA_LOJA]]),
            "percentual_media_loja_6m": limpar_percentual(df_excel.iat[idx_linha, col_idx_map[COLUNA_PERCENTUAL_MEDIA_LOJA]]),
            "valor_media_faixa_faturamento_6m": limpar_valor(df_excel.iat[idx_linha, col_idx_map[COLUNA_VALOR_MEDIA_FAIXA]]),
            "percentual_media_faixa_faturamento_6m": limpar_percentual(df_excel.iat[idx_linha, col_idx_map[COLUNA_PERCENTUAL_MEDIA_FAIXA]]),
            "valor_media_febrafar_6m": limpar_valor(df_excel.iat[idx_linha, col_idx_map[COLUNA_VALOR_MEDIA_FEBRAFAR]]),
            "percentual_media_febrafar_6m": limpar_percentual(df_excel.iat[idx_linha, col_idx_map[COLUNA_PERCENTUAL_MEDIA_FEBRAFAR]])
        }
        
        # Esta regra específica para "Total Líquido" continua a mesma, pois ela sobrescreve o que a função limpar_percentual faz
        if "Total Líquido de Vendas Realizadas" in dados_linha["indicador_nome"]:
            dados_linha["percentual_geral"] = 1.0

        dados_extraidos.append(dados_linha)
        
    return pd.DataFrame(dados_extraidos).dropna(subset=['valor_geral'])

def main():
    conn = None
    try:
        print("Conectando ao banco de dados...")
        conn = mariadb.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Carregando lojas...")
        cursor.execute("SELECT loja_numero, fantasia FROM bronze_lojas")
        lojas_map = {int(numero): nome for numero, nome in cursor.fetchall() if numero is not None}
        print(f"{len(lojas_map)} lojas válidas carregadas com sucesso.")

        todos_os_dados = []
        arquivos_excel = [f for f in os.listdir(PASTA_DOS_ARQUIVOS_EXCEL) if f.endswith('.xlsx') and "financeiro" in f.lower() and not f.startswith('~$')]
        if not arquivos_excel:
            print(f"Nenhum arquivo Excel (.xlsx) encontrado na pasta: '{PASTA_DOS_ARQUIVOS_EXCEL}'")
        else:
            for arquivo in arquivos_excel:
                if "performance" in arquivo.lower():
                    print(f"INFO: Ignorando arquivo de Performance: {arquivo}")
                    continue

                caminho_completo = os.path.join(PASTA_DOS_ARQUIVOS_EXCEL, arquivo)
                df_arquivo_atual = extrair_dados_do_excel(caminho_completo, lojas_map)
                if df_arquivo_atual is not None and not df_arquivo_atual.empty:
                    todos_os_dados.append(df_arquivo_atual)
        
        if not todos_os_dados:
            print("\nNenhum dado válido foi extraído dos arquivos. Encerrando.")
        else:
            df_final_completo = pd.concat(todos_os_dados, ignore_index=True)
            
            ordem_colunas_db = [
                'loja_numero', 'loja_nome', 'data_ref', 'indicador_nome', 
                'valor_geral', 'percentual_geral',
                'valor_media_loja_6m', 'percentual_media_loja_6m',
                'valor_media_faixa_faturamento_6m', 'percentual_media_faixa_faturamento_6m',
                'valor_media_febrafar_6m', 'percentual_media_febrafar_6m'
            ]
            df_final_completo = df_final_completo[ordem_colunas_db]
            df_final_completo = df_final_completo.replace({np.nan: None})

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
                    percentual_geral=VALUES(percentual_geral),
                    valor_media_loja_6m=VALUES(valor_media_loja_6m),
                    percentual_media_loja_6m=VALUES(percentual_media_loja_6m),
                    valor_media_faixa_faturamento_6m=VALUES(valor_media_faixa_faturamento_6m),
                    percentual_media_faixa_faturamento_6m=VALUES(percentual_media_faixa_faturamento_6m),
                    valor_media_febrafar_6m=VALUES(valor_media_febrafar_6m),
                    percentual_media_febrafar_6m=VALUES(percentual_media_febrafar_6m)
            """
            
            dados_para_inserir = [tuple(row) for row in df_final_completo.to_numpy()]
            tamanho_lote = 500
            total_registros = len(dados_para_inserir)

            print(f"\nIniciando inserção/atualização de {total_registros} registros em lotes de {tamanho_lote}...")
            
            registros_processados = 0
            for i in range(0, total_registros, tamanho_lote):
                lote_atual = dados_para_inserir[i:i + tamanho_lote]
                
                cursor.executemany(sql_insert, lote_atual)
                conn.commit()
                
                registros_processados += len(lote_atual)
                print(f"  -> Lote de {len(lote_atual)} registros processado. Total: {registros_processados}/{total_registros}")

            print(f"SUCESSO! Operação concluída na tabela '{TABLE_NAME}'.")

    except mariadb.Error as e:
        print(f"ERRO: {e}")
        if conn and conn.open:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn and conn.open:
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()