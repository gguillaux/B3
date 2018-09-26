# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 22:53:35 2018

@author: Gaston Guillaux
"""

def get_bc_moedas():
    import pandas as pd
    import requests as r
    bc_url = r'https://ptax.bcb.gov.br/ptax_internet/consultarTodasAsMoedas.do?method=consultaTodasMoedas'
    bc_page = r.get(bc_url)
    df_bc = pd.read_html(bc_page.text, thousands='.', decimal=',')[0]
    df_bc.columns = df_bc.iloc[0].values.tolist()
    return df_bc.drop(df_bc.index[0]).drop(df_bc.index[len(df_bc)-2])

#================================================================================================================

def get_b3_indices():
    import pandas as pd
    import requests as r
    import b3_indexes as b3
    from bs4 import BeautifulSoup as bs
    
    titulo = r'<h2>titulo</h2>'
    hr = r'<hr>'
    indices = b3.get_b3_indexes_composition_url()
    indice_tag = r'<a class="dropdown-item" href="#">nome</a>'
    tables_to_publish = ''
    tables_names = ''
    table_classes = 'table table-striped table-dark table-bordered table-hover table-sm'
    for i in indices:
        try:
            comp = indices[i]['composition']
            if 'failed' not in comp:
                name = i
                soup = bs(r.get(comp).text, 'html.parser')
                frame_html = soup.select('iframe[src*="bovespa"]')[0]['src'].replace('pt-br', 'en-us')
                aux_df = pd.read_html(r.get(frame_html).text)[0]
                last_col = aux_df.columns[len(aux_df.columns)-1]
                df = aux_df.sort_values(last_col, ascending=False)
                aux = titulo.replace('titulo', name)
                tables_names += indice_tag.replace('nome', name)
                tables_to_publish += aux + df.drop(df.index[0]).to_html(classes=table_classes, index=False) + hr
        except:
            pass
    return tables_to_publish, tables_names

#================================================================================================================

def load_template():
    template_source = r'C:\Users\Gaston Guillaux\Documents\Python Scripts\B3\indices\template.html'
    with open(template_source, 'rb') as f:
        template = f.read()
    return template.decode(encoding='utf-8')

#================================================================================================================

def main():
    from datetime import datetime
    
    template = load_template()
    pagina = r'C:\Users\Gaston Guillaux\Documents\Python Scripts\B3\indices\index.html'
    bc = get_bc_moedas()
    indices, tag_indices = get_b3_indices()
    p = template.replace('moedasbc', bc.to_html(index=False))
    p = p.replace('listadeindices', indices)
    p = p.replace('dropindices', tag_indices)

    now = datetime.now().strftime(r'Última atualização - %d-%b-%Y %H:%M:%S')
    p = p.replace('lastupdate', now)
    with open(pagina, 'w', encoding='utf-8') as f:
        f.writelines(p)
    