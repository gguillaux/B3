# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 22:00:13 2018

@author: Gaston Guillaux
"""
#export to csv ibovespa composition
def get_ibov():
	from datetime import datetime
	import pandas as pd
	import requests

	now = datetime.now()
	url = r'http://bvmf.bmfbovespa.com.br/indices/ResumoCarteiraQuadrimestre.aspx?Indice=IBOV&idioma=en-us'
	ibov_html = requests.get(url)
	ibov_df_list = pd.read_html(ibov_html.text)
	ibov_df = ibov_df_list[0]
	csv_file = r'c:\temp\auxpy\ibov_' + now.strftime('%Y-%m-%d_%H%M%S.csv')
	ibov_df.to_csv(csv_file, index=False)


#get url of all b3 indexes
def get_b3_indexes_urls():
    from bs4 import BeautifulSoup as bs
    import requests
    
    url = 'http://www.bmfbovespa.com.br/pt_br/produtos/indices/'
    indices = {}
    
    pagina_indices = requests.get(url)
    soup = bs(pagina_indices.text, 'html.parser')
    hrefs = [href for href in soup.select('a[href*="indice"]') if href.getText() == 'Saiba mais']
    for i in hrefs:
        aux = i['href'].replace('./','')
        link = url + aux
        name = i.parent.parent.parent.select('.subheader')[0].getText()
        indices[name] = {}
        indices[name]['url'] = link
    return indices

def get_b3_indexes_carteiras():
    from bs4 import BeautifulSoup as bs    
    import requests
    indexes = get_b3_indexes_urls()
    parent_url = url = 'http://www.bmfbovespa.com.br/pt_br/produtos/indices/'
    
    for index in indexes:
        url = indexes[index]['url']
        pagina = requests.get(url)
        soup = bs(pagina.text, 'html.parser')
        try:
            href = soup.select('a[href*="composicao"]')[0]['href'].replace('./', '')
            indexes[index]['carteira'] =  href
        except:
            indexes[index]['carteira'] = '*** index without composition ***'
    return indexes        