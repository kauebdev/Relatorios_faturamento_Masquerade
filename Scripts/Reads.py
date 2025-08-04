import json, os, sys
import time
import pandas as pd 

def ReadRaw(files_required):
    from Scripts.Padronizes import typePadronize
    '''
    pega o mes e ano de configuração e retorna o arquivo procurado 
    '''
    ano, mes = ReadConfigs()
    folder_ano = f'BRUTOS-{ano}'
    files_finds = []

    # Percorre todas as subpastas
    for file_target in files_required:
        pasta = os.path.join("Data", folder_ano)
        for nome_subfolder in sorted(os.listdir(os.path.join('Data', folder_ano))):
        
        # Extrai o número do mês
            try:
                mes_pasta = int(nome_subfolder.split('-')[0])
            except ValueError:
                continue

            # Parar se chegou no mês desejado
            if mes_pasta == mes:
                caminho_subpasta = os.path.join('Data',folder_ano, nome_subfolder)
                arquivos = os.listdir(caminho_subpasta)
                if file_target in arquivos:
                    file_path = os.path.join(caminho_subpasta, file_target)
                    files_finds.append(file_path)
                elif file_target.endswith("_final.xlsx"):
                    typePadronize(file_target)
                    file_path = os.path.join(caminho_subpasta, file_target)
                    files_finds.append(file_path)
                    time.sleep(0.5)
                break
    if len(files_finds) < 2:
        return pd.read_excel(files_finds[0]) , None
    return pd.read_excel(files_finds[0]), pd.read_excel(files_finds[1])
    
def ReadConfigs():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'Configs', 'resource.json') 
    with open(config_path, 'r') as data:
        config = json.load(data)
        mes = config['month_require']
        ano = config['year_require']
        return ano, mes
