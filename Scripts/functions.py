from datetime import date
import pandas as pd
import os 
import sys

# -- pega o ano a ser utilizado
def GetAno(): 
    try:
        ano = int(input("Digite o ano: ").strip())
        return ano 
    except ValueError:
        print("Ano inválido. Por favor, insira um número inteiro.")
    return None

def GetMes():
    try:
        mes = int(input("Digite o mes: ").strip())
        return mes 
    except ValueError:
        print("mes inválido. Por favor, insira um número inteiro.")
    return None

def GetPeriodo():
    ano = GetAno()        
    mes = GetMes()
    try:
        dia = int(input("Digite o dia: ").strip())
        return date(ano,mes,dia)
    except ValueError:
        print("periodo inválido. Por favor, insira um número inteiro.")
    return None

def PeriodoMenu():
        print("""escolha
              1 - por ano
              2 - por mes 
              3 - de um mes/ano ate um mes/ ano
              """)
        opcao_periodo = int(input("digite o periodo que deja flitrar este relatorio: ").strip())


def EhNovo(mes):
    base_dir =  r'C:\Users\ADMIN\Desktop\kaue\py\faturamento e bi mes a mes\Data'
    
    dfs = []
    
    # Percorrer os anos (BRUTOS-2024, BRUTOS-2025)
    for ano in ["BRUTOS-2024", "BRUTOS-2025"]:
        caminho_ano = os.path.join(base_dir, ano)
        
        if not os.path.exists(caminho_ano):
            continue  # pula se a pasta do ano não existir
        
        # Percorrer as subpastas dentro do ano (ex.: 01-2024, 02-2024, ...)
        for pasta_mes in os.listdir(caminho_ano):
            caminho_arquivo = os.path.join(caminho_ano, pasta_mes, "sh-nfs_final.xlsx")
            
            if os.path.exists(caminho_arquivo):
                df_mes = pd.read_excel(caminho_arquivo)
                dfs.append(df_mes)

    # Juntar tudo em um só DataFrame
    df_all = pd.concat(dfs, ignore_index=True)

    # Ordenar por cliente + data do pedido
    df_all = df_all.sort_values(by=["Clie Cgc Cpf", "Dt. emissão"])

    # Marcar primeira compra real
    df_all["primeira_compra"] = ~df_all["Clie Cgc Cpf"].duplicated()
    
    df_novos = df_all[(df_all["Dt. emissão"].dt.month == mes) &
                (df_all['primeira_compra'] == True)]
    
    return df_novos['Clie Cgc Cpf']