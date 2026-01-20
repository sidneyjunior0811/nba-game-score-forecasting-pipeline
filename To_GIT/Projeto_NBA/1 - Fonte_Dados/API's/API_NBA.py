# %%
import time
import pandas as pd
from datetime import datetime
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.library.http import NBAStatsHTTP
from requests.exceptions import RequestException

# -------------------------------------------------------------------
# 1) Configura User-Agent (evita bloqueio)
# -------------------------------------------------------------------
NBAStatsHTTP.UA_HEADER = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# -------------------------------------------------------------------
# 2) Detecta automaticamente a season atual da NBA
# -------------------------------------------------------------------
def get_current_season():
    today = datetime.today()
    year = today.year
    month = today.month

    # NBA season começa em outubro
    if month >= 10:
        return f"{year}-{str(year + 1)[-2:]}"
    else:
        return f"{year - 1}-{str(year)[-2:]}"

# -------------------------------------------------------------------
# 3) Baixa apenas a season atual com retries
# -------------------------------------------------------------------
def fetch_current_season(retries=5, delay=5):
    season = get_current_season()
    print(f"📅 Season atual detectada: {season}")

    for attempt in range(1, retries + 1):
        try:
            print(f"🔄 Baixando season {season} (tentativa {attempt})")

            finder = leaguegamefinder.LeagueGameFinder(
                season_nullable=season
            )

            df = finder.get_data_frames()[0]
            df["SEASON"] = season

            print(f"✔ OK: {len(df)} registros baixados")
            return df

        except RequestException as e:
            print(f"⚠ Erro de conexão: {e} — retry em {delay}s")
            time.sleep(delay)

        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            break

    print("❌ Falha ao baixar a season atual")
    return pd.DataFrame()

# -------------------------------------------------------------------
# 4) Executar
# -------------------------------------------------------------------
games = fetch_current_season()


# %%
import numpy as np
games = games.replace([np.nan, np.inf, -np.inf], None)

# %%
def classificar_jogo(game_id):
    if game_id.startswith('001'):
        return 'Preseason'
    elif game_id.startswith('002'):
        return 'RegularSeason'
    elif game_id.startswith('003'):
        return 'IST'
    elif game_id.startswith('004'):
        return 'Playoffs'
    elif game_id.startswith('005'):
        return 'PlayIn'
    elif game_id.startswith('006'):
        return 'AllStar'
    else:
        return 'Unknown'

games['SeasonType'] = games['GAME_ID'].apply(classificar_jogo)

# %%
import pyodbc
# Conexão com SQL Server
conn = pyodbc.connect('Driver={SQL Server};Server=JUNIOR;Database=NBA;Trusted_Connection=yes;')
cursor = conn.cursor()

# Enviar cada linha do DataFrame
for index, row in games.iterrows():
    cursor.execute("EXEC PROC_base_api_Basquete ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?", 
                row['SEASON_ID'], row['TEAM_ID'], row['TEAM_ABBREVIATION'], row['TEAM_NAME'], row['GAME_ID'], row['GAME_DATE'],
                row['MATCHUP'], row['WL'], row['MIN'], row['PTS'], row['FGM'],row['FGA'],row['FG_PCT'],row['FG3M'],row['FG3A'],
                row['FG3_PCT'],row['FTM'],row['FTA'],row['FT_PCT'],row['OREB'],row['DREB'],row['REB'],row['AST'],row['STL'],
                row['BLK'],row['TOV'],row['PF'],row['PLUS_MINUS'],row['SEASON'],row['SeasonType'])
conn.commit()
conn.close()
print("Dados enviados para o SQL Server!")


