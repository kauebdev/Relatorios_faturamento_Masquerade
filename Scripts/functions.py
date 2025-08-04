from datetime import date

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


