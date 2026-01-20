# %%
import requests
import pandas as pd

# URL da API da ESPN para standings
url = "https://site.web.api.espn.com/apis/v2/sports/basketball/nba/standings"
params = {
    "region": "us",
    "lang": "en",
    "contentorigin": "espn",
    "type": "0"  # 0 para temporada regular
}

response = requests.get(url, params=params)
data = response.json()

# %%
tabela_classificacao = []

# Processar os dados
if response.status_code == 200:
    for conference in data['children']:

        for API_NBA in conference['standings']['entries']:
            time = API_NBA['team']['displayName']
            logo = API_NBA['team']['logos']
            for logoTime in logo:
                logoTime = logoTime.get("href")
            

            for status in API_NBA['stats']:
                if status['name'] == 'winPercent':
                    percVitoria = status['value']

                if status['name'] == 'avgPointsAgainst':
                    pontos_sofridos = status['value']

                if status['name'] == 'avgPointsFor':
                    pontos_feitos = status['value'] 

                if status['name'] == 'gamesBehind':
                    DiferencaJogosLider = status['value']    
        
                if status['name'] == 'wins':
                    Vitorias = status['value']
        
                if status['name'] == 'losses':
                    Derrota = status['value']
        
                if status['name'] == 'Home':
                    JogosCasa = status['summary']
        
                if status['name'] == 'Road':
                    JogosFora = status['summary']
        
                if status['name'] == 'vs. Div.':
                    ConfrontoDivisao = status['summary']
        
                if status['name'] == 'vs. Conf.':
                    ConfrontoConferencia = status['summary']

            tabela_classificacao.append([time, percVitoria, pontos_sofridos,pontos_feitos, DiferencaJogosLider, Vitorias, Derrota, JogosCasa, JogosFora, ConfrontoDivisao, ConfrontoConferencia,logoTime])

# %%
columns = ['time','percVitoria','pontos_sofridos','pontos_feitos','DiferencaJogosLider','Vitorias','Derrota','JogosCasa','JogosFora','ConfrontoDivisao','ConfrontoConferencia','logoTime']

# %%
df = pd.DataFrame(tabela_classificacao,columns=columns)

# %%
import pyodbc
# Conexão com SQL Server
conn = pyodbc.connect('Driver={SQL Server};Server=JUNIOR;Database=NBA;Trusted_Connection=yes;')
cursor = conn.cursor()

# Enviar cada linha do DataFrame
for index, row in df.iterrows():
    cursor.execute("EXEC PROC_Classificacao ?,?,?,?,?,?,?,?,?,?,?,?", 
                row['time'], row['percVitoria'], row['pontos_sofridos'], row['pontos_feitos'], row['DiferencaJogosLider'], row['Vitorias'],row['Derrota'], row['JogosCasa'], row['JogosFora'], row['ConfrontoDivisao'], row['ConfrontoConferencia'],row['logoTime'])

conn.commit()
conn.close()
print("Dados enviados para o SQL Server!")


