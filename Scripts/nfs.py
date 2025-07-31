import json, os
import pandas as pd 

def PadronizeNotasFiscais():
    '''
    corrigir cod vendedores bling
    nr de pedido
 
    '''


    # -- 1 - le os arquivos
    df_nfs_bling = pd.read_excel(r"..\Data\01-01-23_08-07-25\sh-nfs_bling.xlsx")
    df_nfs_infosoft = pd.read_excel(r"..\Data\01-01-23_08-07-25\sh-nfs_infosoft.xlsx")

    # -- 2 - padroniza as colunas para evitar complicações
    df_nfs_bling.rename(columns={'Data de emissão':'Dt. emissão', 
                                'Data de Saída/Entrada':'Dt Sai Ent', 
                                'Número':'Nr. nota', 
                                'CNPJ/CPF':'Clie Cgc Cpf',
                                'Código do vendedor':'Cd Vendedor', 
                                'Desconto':'Vl Total Desc', 
                                'Valor total líquido':'Vl Total Nota'
                                },inplace=True)

    # -- 3 -  junta as duas df 
    df_nfs_masquerade = pd.concat([df_nfs_bling,df_nfs_infosoft], axis=0)

    # # -- 4 - arrumando vendedores !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # df_nfs_masquerade['Cd Vendedor'] = df_nfs_masquerade['Cd Vendedor'].fillna('').astype(str).str.strip()

    # df_nfs_masquerade, logs = mapear_vendedores_por_similaridade(df_nfs_masquerade, df_vendedores_masquerade)


    # -- 5 - padroniza os tipos e filtr
    df_nfs_masquerade['Clie Cgc Cpf'] = (
        df_nfs_masquerade['Clie Cgc Cpf']
        .astype(str)
        .str.strip()                  # remove espaços antes/depois
        .str.replace(r'\s+', '', regex=True)  # remove espaços internos
    )
    ice = ['27.191.195/0001-50',
    '18.848.204/0001-42',
    '08.913.661/0001-10',
    '11.990.266/0001-45',
    '05.012.654/0001-59',
    '04.466.924/0001-39',
    '44.667.686/0001-44',
    '45.385.860/0001-29',
    '41.400.310/0001-80' ]
    df_nfs_masquerade = df_nfs_masquerade[~df_nfs_masquerade['Clie Cgc Cpf'].isin(ice)]
    df_nfs_masquerade['Dt Sai Ent'] = pdDatetime(df_nfs_masquerade['Dt Sai Ent'] , dayfirst=True)
    df_nfs_masquerade['Dt. emissão'] = pdDatetime(df_nfs_masquerade['Dt. emissão'], dayfirst=True)
    df_nfs_masquerade['Vl Total Desc'] = df_nfs_masquerade['Vl Total Desc'].astype(str).str.replace(',','')
    df_nfs_masquerade['Vl Total Nota'] = df_nfs_masquerade['Vl Total Nota'].astype(str).str.replace(',','')
    df_nfs_masquerade['Vl Total Desc'] = pdNumeric(df_nfs_masquerade['Vl Total Desc'],errors='coerce')
    df_nfs_masquerade['Vl Total Nota'] =  pdNumeric(df_nfs_masquerade['Vl Total Nota'],errors='coerce')
    df_nfs_masquerade['Nr Pedido'] =  pdNumeric(df_nfs_masquerade['Nr Pedido'],errors='coerce')



def ReadNotasFiscais():
    '''
    pega o mes e ano de configuração e retrona o arquivo de nfs relativo
    '''
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'Configs', 'resource.json')
    with open(config_path, 'r') as data:
        config = json.load(data)
        mes = config['month_require']   
        ano = config['year_require']
        print(ano)
    file_path = os.path.join(script_dir, '..', 'Data', f'BRUTOS-{ano}', f'{mes:02d}-{ano}', 'sh-nfs_infosoft.xlsx')
    return pd.read_excel(file_path)

    