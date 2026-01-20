# %%
from nba_api.stats.endpoints import scoreboardv2
import pandas as pd

# ==========================
# 1) Chamada da API
# ==========================
scoreboard = scoreboardv2.ScoreboardV2()
games = scoreboard.game_header.get_data_frame()
teams = scoreboard.line_score.get_data_frame()

# ==========================
# 2) Filtra apenas jogos futuros
# ==========================

games = games[(games['GAME_STATUS_ID'] == 1) | (games['GAME_STATUS_ID'] == 2) | (games['GAME_STATUS_ID'] == 3)]

# %%
teams = teams.sort_values(['GAME_ID', 'TEAM_ID']).reset_index(drop=True)

# %%
teams['NAME_TEAM'] = teams['TEAM_CITY_NAME'] + ' ' + teams['TEAM_NAME']

# %%
games = games[['GAME_ID','GAME_STATUS_TEXT','GAME_DATE_EST','GAMECODE','HOME_TEAM_ID','VISITOR_TEAM_ID','ARENA_NAME','SEASON','GAME_STATUS_ID']]
games.rename(columns={'GAME_DATE_EST':'GAME_DATE','GAME_STATUS_TEXT':'GAME_HORA','VISITOR_TEAM_ID':'AWAY_TEAM_ID','GAME_STATUS_ID':'GAME_STATUS_PARTIDA'},inplace=True)

# %%
games = (
    games
    .merge(
        teams[['TEAM_ID', 'NAME_TEAM', 'TEAM_ABBREVIATION']],
        left_on='HOME_TEAM_ID',
        right_on='TEAM_ID',
        how='left'
    )
    .rename(columns={
        'TEAM_NAME': 'HOME_TEAM_NAME',
        'TEAM_ABBREVIATION': 'HOME_TEAM_ABBR'
    })
    .drop(columns='TEAM_ID')
    .merge(
        teams[['TEAM_ID', 'NAME_TEAM', 'TEAM_ABBREVIATION']],
        left_on='AWAY_TEAM_ID',
        right_on='TEAM_ID',
        how='left'
    )
    .rename(columns={
        'TEAM_NAME': 'AWAY_TEAM_NAME',
        'TEAM_ABBREVIATION': 'AWAY_TEAM_ABBR'
    })
    .drop(columns='TEAM_ID')
)


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
games = games[['HOME_TEAM_ID','NAME_TEAM_x','HOME_TEAM_ABBR','GAME_ID','GAME_DATE','GAME_HORA','AWAY_TEAM_ID','NAME_TEAM_y','AWAY_TEAM_ABBR','ARENA_NAME','SEASON','GAME_STATUS_PARTIDA','SeasonType']]

# %%
import pyodbc

conn = pyodbc.connect(
    'Driver={SQL Server};'
    'Server=JUNIOR;'
    'Database=NBA;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

for _, row in games.iterrows():
    cursor.execute("""
        EXEC dbo.PROC_AtualizacaoJogosHoje
            ?,?,?,?,?,?,?,?,?,?,?,?,? """,
        row['HOME_TEAM_ID'],
        row['NAME_TEAM_x'],
        row['HOME_TEAM_ABBR'],
        row['GAME_ID'],
        row['GAME_DATE'],
        row['GAME_HORA'],
        row['AWAY_TEAM_ID'],
        row['NAME_TEAM_y'],
        row['AWAY_TEAM_ABBR'],
        row['ARENA_NAME'],
        row['SEASON'],
        row['GAME_STATUS_PARTIDA'],
        row['SeasonType']
    )

conn.commit()
conn.close()

print("Dados enviados para o SQL Server!")



