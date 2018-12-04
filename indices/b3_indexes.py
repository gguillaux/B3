# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 22:00:13 2018

@author: Gaston Guillaux
"""
import os
import time
import shutil
import requests
import pandas as pd
from threading import Thread
from datetime import datetime
from bs4 import BeautifulSoup as bs


#export to csv ibovespa composition
def get_ibov():
	now = datetime.now()
	url = r'http://bvmf.bmfbovespa.com.br/indices/ResumoCarteiraQuadrimestre.aspx?Indice=IBOV&idioma=en-us'
	ibov_html = requests.get(url)
	ibov_df_list = pd.read_html(ibov_html.text)
	ibov_df = ibov_df_list[0]
	csv_file = r'c:\temp\auxpy\ibov_' + now.strftime('%Y-%m-%d_%H%M%S.csv')
	ibov_df.to_csv(csv_file, index=False)

#==================================================================================================

#get url of all b3 indexes
def get_b3_indexes_urls():    
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

def get_url(index, indexes):
    url = indexes[index]['url']
    pagina = requests.get(url)
    soup = bs(pagina.text, 'html.parser')
    try:
        href = soup.select('a[href*="composicao"]')[0]['href'].replace('./', '')
        indexes[index]['composition'] = trim_url(url) +  href
    except Exception as e:
        indexes[index]['composition'] = '*** failed to get composition *** . Error message = ' + str(e)

def get_b3_indexes_composition_url():
    indexes = get_b3_indexes_urls()
    
    threads = []
    for index in indexes:
        t = Thread(target=get_url, args=([index, indexes]))
        threads.append(t)
        t.start()
    [t.join() for t in threads]
    return indexes

#==================================================================================================

def get_composition(i, indexes, csv_path):
    try:
       comp = indexes[i]['composition']
       if 'failed' not in comp:
           soup = bs(requests.get(comp).text, 'html.parser')
           frame_html = soup.select('iframe[src*="bovespa"]')[0]['src'].replace('pt-br', 'en-us')
           print(frame_html)
           comp_df = pd.read_html(requests.get(frame_html).text)[0]
           last_col = comp_df.columns[len(comp_df.columns)-1]
           agora = datetime.now().strftime('_%d-%b-%Y_%H%M%S.csv')
           df_index = comp_df.sort_values(last_col, ascending=False)
           df_index.to_csv(os.path.join(csv_path, i + agora), index=False)
           indexes[i]['dataframe'] = df_index
       else:
           print(i + ' failed')
           indexes[i]['dataframe'] = '*** no dataframe ***'
    except:
        indexes[i]['dataframe'] = '*** no dataframe ***'


def get_index_composition_csv(indexes):
    
    csv_path = r'c:\temp\auxpy' 
    shutil.rmtree(csv_path, ignore_errors=True)
    os.makedirs(csv_path, exist_ok=True)
    
    threads = []
    for i in indexes:
        t = Thread(target=get_composition, args=([i, indexes, csv_path]))
        threads.append(t)
        t.start()
    [t.join() for t in threads]
     
#==================================================================================================

def trim_url(url):
    last_slash = url[::-1].find('/')
    clean_url = url[:len(url) - last_slash]
    return clean_url

if __name__ == '__main__':
    start = time.perf_counter()
    urls = get_b3_indexes_composition_url()
    get_index_composition_csv(urls)
    end = time.perf_counter()
    print('{} seconds'.format(end-start))