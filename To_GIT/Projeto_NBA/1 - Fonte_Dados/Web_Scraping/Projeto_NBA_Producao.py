# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# %%
link = 'https://nba.footybite.to/'
pagina = requests.get(link)
soup = BeautifulSoup(pagina.text, 'html')

# %%
jogos = soup.find_all('div', class_='col-md-5 col-12 m-md-2 my-2 p-2 rounded bg-white pointer hover-box')

# %%
jogos_lista = []
for jogo in jogos:
    partida = jogo.find('a')['href']
    partida = partida.split('/')[-2].replace('-', ' ')

    linkJogo = jogo.find('a')['href']

    tempoJogo = jogo.find('p', class_='bg-light-gray d-inline-block rounded-pill font-weight-bolder py-1 px-2 font-14')
    tempoJogo = tempoJogo.text
    tempoJogo = tempoJogo.strip()
    
    placarJogo = jogo.find_all('div', class_='my-2')
    
    if len(placarJogo) == 2:
        placarCasa = placarJogo[0].find('span', class_='score')
        placarFora = placarJogo[1].find('span', class_='score')
        imagemTimeCasa = placarJogo[0].find('img')['src']
        imagemTimeFora = placarJogo[1].find('img')['src']
        
        placarCasa = placarCasa.text.strip() if placarCasa else 'Sem Placar'
        placarFora = placarFora.text.strip() if placarFora else 'Sem Placar'
        placarJogo = f"{placarCasa} - {placarFora}"
        imagemTime = f"{'https://nba.footybite.to'+imagemTimeCasa} - {'https://nba.footybite.to'+imagemTimeFora}"


    jogos_lista.append([partida, 'https://nba.footybite.to'+linkJogo, tempoJogo,placarJogo, imagemTime])

# %%
colunas = ['partida', 'linkJogo', 'tempoJogo', 'placarJogo','imagemTime']
df = pd.DataFrame(jogos_lista, columns=colunas)

# %%
id_partida = []
for id in df['linkJogo']:
    id_partida.append(re.search(r'\d+$',id).group())

# %%
df['id_partida'] = id_partida

# %%
df = df[['id_partida','partida', 'linkJogo', 'tempoJogo', 'placarJogo','imagemTime']]
df = df.sort_values(by='id_partida', ascending= False)

# %%
import pyodbc
# Conexão com SQL Server
conn = pyodbc.connect('Driver={SQL Server};Server=JUNIOR;Database=NBA;Trusted_Connection=yes;')
cursor = conn.cursor()

# Enviar cada linha do DataFrame
for index, row in df.iterrows():
    cursor.execute("EXEC atualizacao_Jogos ?, ?, ?, ?,?,?", 
                row['id_partida'], row['partida'], row['linkJogo'], row['tempoJogo'], row['placarJogo'], row['imagemTime'])

conn.commit()
conn.close()
print("Dados enviados para o SQL Server!")


