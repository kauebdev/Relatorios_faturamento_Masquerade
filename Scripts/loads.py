import json, os
import pandas as pd 

def LoadFinal(df_final, file_name):
    from Scripts.Reads import ReadConfigs
    '''
    pega o mes e ano de configuração e retorna o arquivo procurado 
    '''
    ano, mes = ReadConfigs()
    folder_ano = f'BRUTOS-{ano}'
    
    # Percorre todas as subpastas
    for nome_subfolder in sorted(os.listdir(os.path.join('Data', folder_ano))):
        
        # Extrai o número do mês
        try:
            mes_pasta = int(nome_subfolder.split('-')[0])
        except ValueError:
            continue

        # Parar se chegou no mês desejado
        if mes_pasta == mes:
            caminho_subpasta = os.path.join('Data',folder_ano, nome_subfolder)
            break
    file_path = os.path.join(caminho_subpasta,file_name)
    df_final.to_excel(file_path, index=False)
    