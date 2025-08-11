import os, json, sys
from pandas import to_numeric as pdNumeric
from pandas import to_datetime as pdDatetime
import pandas as pd 

def typePadronize(file_target):
    from Scripts.Reads import ReadConfigs, ReadRaw
    from Scripts.loads import LoadFinal
    type = file_target.split("_")[0]
    match type:
        case 'sh-nfs':
            PadronizeNotasFiscais()
        case 'sh-pedidos':
            PadronizePedidos()    

def PadronizeNotasFiscais(): # ✔️
    '''
    corrigir cod vendedores bling
    nr de pedido
    '''
    from Scripts.Reads import ReadRaw
    from Scripts.loads import LoadFinal
    # -- 1 - le os arquivos
    df_nfs_infosoft, df_nfs_bling = ReadRaw(['sh-nfs_infosoft.xlsx','sh-nfs_bling.xlsx'])
    if df_nfs_infosoft is not None:
        if df_nfs_bling is not None:
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
            # no fuuturo fazer direro o masuerdae ser igual ao o infosfot para melhor viusalização de codgio
            df_nfs_masquerade = pd.concat([df_nfs_bling,df_nfs_infosoft], axis=0)

            # # -- 4 - arrumando vendedores !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # df_nfs_masquerade['Cd Vendedor'] = df_nfs_masquerade['Cd Vendedor'].fillna('').astype(str).str.strip()

            # df_nfs_masquerade, logs = mapear_vendedores_por_similaridade(df_nfs_masquerade, df_vendedores_masquerade)
        else:
            df_nfs_masquerade = df_nfs_infosoft.copy()

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
        # df_nfs_masquerade['Vl Total Desc'] = df_nfs_masquerade['Vl Total Desc'].astype(str).str.replace(',','')
        df_nfs_masquerade['Vl Total Nota'] = df_nfs_masquerade['Vl Total Nota'].astype(str).str.replace(',','')
        # df_nfs_masquerade['Vl Total Desc'] = pdNumeric(df_nfs_masquerade['Vl Total Desc'],errors='coerce')
        df_nfs_masquerade['Vl Total Nota'] =  pdNumeric(df_nfs_masquerade['Vl Total Nota'],errors='coerce')
        df_nfs_masquerade['Nr Pedido'] =  pdNumeric(df_nfs_masquerade['Nr Pedido'],errors='coerce')
        
    LoadFinal(df_nfs_masquerade,'sh-nfs_final.xlsx')
        
def PadronizePedidos(): # ✔️
    from Scripts.Reads import ReadRaw
    from Scripts.loads import LoadFinal
    # lendos os aqruivos 
    df_pedidos_e_produtos_infosoft, df_pedidos_e_produtos_bling = ReadRaw(["sh-pedidos-e-produtos-infosoft.xlsx","sh-pedidos-e-produtos-bling.xlsx"])
    
    
    if df_pedidos_e_produtos_infosoft is not None:
        # pegando os pedidos da infosoft
        df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft.dropna(how='all')
        df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft[df_pedidos_e_produtos_infosoft['Nr. pedido'].isna()]
        df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft[df_pedidos_e_produtos_infosoft['CNPJ - CPF'] != '- Nr Pedido']
        df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft.drop(['Nr. pedido','Unnamed: 10'], axis=1)
        df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft.rename(columns={'CNPJ - CPF'	: 'Nr. pedido','Dt. pedido'	: 'Cd Cliente','Pedido de venda - Vl. desconto'	: 'Dt. pedido', 'Unnamed: 9'	: 'Vl. total','Vl. total' : 'NONE'})
        df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft[['Nr. pedido', 'Cd Cliente', 'Dt. pedido','Vl. total']]
        df_pedidos_e_produtos_infosoft['Dt. pedido'] = pd.to_datetime(df_pedidos_e_produtos_infosoft['Dt. pedido'], dayfirst=True)
        df_pedidos_e_produtos_infosoft['Vl. total'] = (
            df_pedidos_e_produtos_infosoft['Vl. total']
            .astype(str)
            .  str.replace(',', '', regex=False)) # remove separador de milhar  
        df_pedidos_e_produtos_infosoft['Vl. total'] = pd.to_numeric(df_pedidos_e_produtos_infosoft['Vl. total'])
        df_pedidos_infosoft = df_pedidos_e_produtos_infosoft.groupby(['Nr. pedido', 'Cd Cliente', 'Dt. pedido'])['Vl. total'].sum().reset_index()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        pasta_dados = os.path.join(base_dir, '..', 'Data', 'BRUTOS-GERAIS','CLIENTES')
        df_clients_infosoft = pd.read_excel(os.path.join(pasta_dados, 'sh-clientes_infosoft.xlsx'))
        df_pedidos_infosoft['Cd Cliente'] = df_pedidos_infosoft['Cd Cliente'].astype(str)
        df_clients_infosoft['Cd Cliente'] = df_clients_infosoft['Cd Cliente'].astype(str)
        df_pedidos_infosoft = df_pedidos_infosoft.merge(df_clients_infosoft[['Cd Cliente', 'Cgc Cpf']],
                                                        on='Cd Cliente', how='left' ).drop('Cd Cliente', axis=1) 
        if df_pedidos_e_produtos_bling is not None:
            # pegando os pedidos do bling
            df_pedidos_e_produtos_bling = df_pedidos_e_produtos_bling[['Número do pedido', 'CPF/CNPJ', 'Data','Valor total']]
            df_pedidos_e_produtos_bling['Data'] = pd.to_datetime(df_pedidos_e_produtos_bling['Data'], unit='D', origin='1899-12-30')
            df_pedidos_bling = df_pedidos_e_produtos_bling.groupby(['Número do pedido', 'CPF/CNPJ', 'Data'])['Valor total'].sum().reset_index()
    
            df_pedidos_bling.rename(columns={'CPF/CNPJ':'Cgc Cpf', 
                                                'Valor total': 'Vl. total',
                                                'Data': 'Dt. pedido',
                                                'Número do pedido': 'Nr. pedido'
                                                },inplace=True)

            df_pedidos_masquerade = pd.concat([df_pedidos_infosoft,df_pedidos_bling], axis=0)
        else:
            df_pedidos_masquerade = df_pedidos_infosoft.copy()
        # padronização com as nf
        df_pedidos_masquerade.rename(columns={'Cgc Cpf':'Clie Cgc Cpf', 
                                            'Vl. total': 'Vl venda',
                                            'Nr. pedido': 'Nr Pedido',
                                            'Dt. pedido': 'Dt. emissão'
                                            },inplace=True)

        # -- 5 - padroniza os tipos e filtr
        df_pedidos_masquerade['Clie Cgc Cpf'] = (
            df_pedidos_masquerade['Clie Cgc Cpf']
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
        df_pedidos_masquerade = df_pedidos_masquerade[~df_pedidos_masquerade['Clie Cgc Cpf'].isin(ice)]

        df_pedidos_masquerade['Nr Pedido'] = pdNumeric(df_pedidos_masquerade['Nr Pedido'])
        df_pedidos_masquerade['Vl venda'] = df_pedidos_masquerade['Vl venda'].astype(str).str.replace(',','')
        df_pedidos_masquerade['Vl venda'] = pdNumeric(df_pedidos_masquerade['Vl venda'])
        df_pedidos_masquerade['Dt. emissão'] =  pd.to_datetime(df_pedidos_masquerade['Dt. emissão'], dayfirst=True, )
    
    LoadFinal(df_pedidos_masquerade,"sh-pedidos_final.xlsx")

def PadronizeClientes(): # ✔️
    # -- 1 lendo arquivos
    # Caminho absoluto da pasta onde o script está localizado
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pasta_dados = os.path.join(base_dir, '..', 'Data', 'BRUTOS-GERAIS','CLIENTES')
    df_clients_bling = pd.read_excel(os.path.join(pasta_dados, 'sh-clientes_bling.xlsx'))
    df_clients_infosoft = pd.read_excel(os.path.join(pasta_dados, 'sh-clientes_infosoft.xlsx'))
    df_clients_infosoft.drop('Cd Cliente' , axis=1, inplace=True)
    # -- 2 - padroniza os nomes para maior facilidade
    df_clients_infosoft.rename(columns={'Cgc Cpf':'Clie Cgc Cpf'}, 
                                    inplace=True)
    df_clients_bling.rename(columns={'CPF/CNPJ': 'Clie Cgc Cpf',
                                    'Nome':'Descrição', 
                                    'Endereço': 'Endereco',
                                    'UF':'Cd Uf', 
                                    'Cidade':'Nm Cidade', 
                                    'Bairro':'Bairro',
                                    'Cliente desde':'Dt Cadastro', 
                                    'Email':'E Mail'
                                    }, inplace=True)

    # -- 3 - faz o full join 
    df_clientes_merge = pd.merge(df_clients_infosoft,df_clients_bling,
                                    on='Clie Cgc Cpf',   # chave primaria
                                    how='outer',    # full outer join no pandas       
                                    suffixes=('_infosoft','_bling')) # renomeias o sufixo das colunas (col1_df1,col2_df2...)

    # -- 4 - filtrando para todos os clients ou seja '''full join com priorização do df1'''
    cols = ['Descrição', 'Endereco', 'Cd Uf','Nm Cidade', 'Bairro', 'Dt Cadastro','E Mail'] # colunas que quero manter (na esquerda)
    for col in cols: 
        df_clientes_merge[col] = df_clientes_merge[f'{col}_infosoft'].combine_first(df_clientes_merge[f'{col}_bling']) # where quando a esquerda for vazia colca conteudo da direita, colca tudo na nova coluna 
        
    df_clientes_masquerade = df_clientes_merge[['Clie Cgc Cpf'] + cols] # atribui a df final o conteudo completo nas colunas novas sem esquecer da chave primeira
    
    df_clientes_masquerade.to_excel(os.path.join(pasta_dados, 'sh-clientes_final.xlsx'))

def PadronizeProdutos():
    from Scripts.Reads import ReadRaw
    from Scripts.loads import LoadFinal
    # lendos os aqruivos 
    df_pedidos_e_produtos_infosoft, df_pedidos_e_produtos_bling = ReadRaw(["sh-pedidos-e-produtos-infosoft.xlsx","sh-pedidos-e-produtos-bling.xlsx"])
    
    # pegando os produtos do bling
    df_pedidos_e_produtos_bling = df_pedidos_e_produtos_bling[['Número do pedido', 'CPF/CNPJ', 'Data','Código','Descrição','Preço unitário', 'Quantidade']]
    df_pedidos_e_produtos_bling['Data'] = pd.to_datetime(df_pedidos_e_produtos_bling['Data'], unit='D', origin='1899-12-30')
    df_produtos_bling = df_pedidos_e_produtos_bling.copy()
    
    # pegando os produtos da infosoft
    df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft.dropna(how='all')
    df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft[df_pedidos_e_produtos_infosoft['Nr. pedido'].isna()]
    df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft[df_pedidos_e_produtos_infosoft['CNPJ - CPF'] != '- Nr Pedido']
    df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft.drop(['Nr. pedido','Unnamed: 10'], axis=1)
    df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft.rename(columns={'CNPJ - CPF'	: 'Nr. pedido','Dt. pedido'	: 'Cd Cliente','Pedido de venda - Vl. desconto'	: 'Dt. pedido', 'Unnamed: 9'	: 'Vl. total','Vl. total' : 'NONE', 'Unnamed: 8': 'quant', 'Unnamed: 6': 'desc', 'Unnamed: 7': 'Vl unitario', 'Unnamed: 5':'cod_prod' })
    df_pedidos_e_produtos_infosoft = df_pedidos_e_produtos_infosoft[['Nr. pedido', 'Cd Cliente', 'Dt. pedido','quant', 'desc',  'Vl unitario', 'cod_prod']]
    df_pedidos_e_produtos_infosoft['Dt. pedido'] = pd.to_datetime(df_pedidos_e_produtos_infosoft['Dt. pedido'], dayfirst=True)
    df_pedidos_e_produtos_infosoft['Vl unitario'] = (df_pedidos_e_produtos_infosoft['Vl unitario'].astype(str).str.replace(',', '', regex=False))
    df_pedidos_e_produtos_infosoft['Vl unitario'] = pd.to_numeric(df_pedidos_e_produtos_infosoft['Vl unitario'])
    df_produtos_infosoft = df_pedidos_e_produtos_infosoft.copy()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pasta_dados = os.path.join(base_dir, '..', 'Data', 'BRUTOS-GERAIS','CLIENTES')
    df_clients_infosoft = pd.read_excel(os.path.join(pasta_dados, 'sh-clientes_infosoft.xlsx'))
    df_produtos_infosoft['Cd Cliente'] = df_produtos_infosoft['Cd Cliente'].astype(str)
    df_clients_infosoft['Cd Cliente'] = df_clients_infosoft['Cd Cliente'].astype(str)
    df_produtos_infosoft = df_produtos_infosoft.merge(df_clients_infosoft[['Cd Cliente', 'Cgc Cpf']],
                                                    on='Cd Cliente', how='left' ).drop('Cd Cliente', axis=1)

    if df_produtos_infosoft is not None:
        if df_produtos_bling is not None:       
            df_produtos_bling.rename(columns={'Número do pedido': 'Nr. pedido',
                                      'CPF/CNPJ': 'Cgc Cpf',
                                      'Data': 'Dt. pedido',
                                      'Código': 'cod_prod',
                                      'Descrição': 'desc',
                                      'Preço unitário': 'Vl unitario', 
                                      'Quantidade':'quant'}, inplace=True)

            df_produtos_masquerade = pd.concat([df_produtos_infosoft,df_produtos_bling], axis=0)
        else:
            df_produtos_masquerade = df_produtos_infosoft.copy()
        
        df_produtos_masquerade['Nr. pedido'] = pdNumeric(df_produtos_masquerade['Nr. pedido'])
        df_produtos_masquerade['Dt. pedido'] =  pd.to_datetime(df_produtos_masquerade['Dt. pedido'], dayfirst=True, )
    
    LoadFinal(df_produtos_masquerade,"sh-produtos_final.xlsx")

