from datetime import date
from rapidfuzz import process, fuzz

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


def mapear_vendedores_por_similaridade(df, df_ref, threshold=85):

    logs = []

    nomes_ref = df_ref['Nm Vendedor'].tolist()

    for idx, nome in df['Cd Vendedor'].items():
        if not isinstance(nome, str) or nome.strip() == '':
            continue

        melhor, score, _ = process.extractOne(nome, nomes_ref, scorer=fuzz.partial_ratio)

        if score >= threshold:
            codigo = df_ref.loc[df_ref['Nm Vendedor'] == melhor, 'Cd Vendedor'].values[0]
            logs.append(f"{nome} → {melhor} → {codigo}")
            df.at[idx, 'Cd Vendedor'] = codigo
        else:
            logs.append(f"{nome} → [sem correspondência acima de {threshold}]")

    return df, logs
