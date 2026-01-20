# %%
import pyodbc
import pandas as pd

server_name = "JUNIOR"  # nome do servidor retornado
database_name = "NBA"

connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={database_name};Trusted_Connection=yes"

conn = pyodbc.connect(connection_string)

df = pd.read_sql("SELECT * FROM TB_Base_API", conn)

# %%
df_RegularSeason = df[df['SeasonType'] == 'RegularSeason'].sort_values('GAME_DATE', ascending=False)
df_RegularSeason_copy = df_RegularSeason.copy()

# %%
def generate_team_features_side(df, side):
    team_col = f"TEAM_ID_{side}"

    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df = df.sort_values([team_col, "GAME_DATE"])

    # Rolling 5
    df[f"rolling_pts_5_{side}"] = (
        df.groupby(team_col)[f"PTS_{side}"]
          .shift(1)
          .rolling(5, min_periods=3)
          .mean()
    )

    df[f"rolling_plus_minus_5_{side}"] = (
        df.groupby(team_col)[f"PLUS_MINUS_{side}"]
          .shift(1)
          .rolling(5, min_periods=3)
          .mean()
    )

    # Rolling 7
    df[f"rolling_oreb_7_{side}"] = (
        df.groupby(team_col)[f"OREB_{side}"]
          .shift(1)
          .rolling(7, min_periods=4)
          .mean()
    )

    df[f"rolling_dreb_7_{side}"] = (
        df.groupby(team_col)[f"DREB_{side}"]
          .shift(1)
          .rolling(7, min_periods=4)
          .mean()
    )

    df[f"rolling_ast_7_{side}"] = (
        df.groupby(team_col)[f"AST_{side}"]
          .shift(1)
          .rolling(7, min_periods=4)
          .mean()
    )

    df[f"rolling_tov_7_{side}"] = (
        df.groupby(team_col)[f"TOV_{side}"]
          .shift(1)
          .rolling(7, min_periods=4)
          .mean()
    )

    # Rolling 10
    df[f"rolling_fg_pct_10_{side}"] = (
        df.groupby(team_col)[f"FG_PCT_{side}"]
          .shift(1)
          .rolling(10, min_periods=5)
          .mean()
    )

    df[f"rolling_fg3_pct_10_{side}"] = (
        df.groupby(team_col)[f"FG3_PCT_{side}"]
          .shift(1)
          .rolling(10, min_periods=5)
          .mean()
    )

    df[f"rolling_ft_pct_10_{side}"] = (
        df.groupby(team_col)[f"FT_PCT_{side}"]
          .shift(1)
          .rolling(10, min_periods=5)
          .mean()
    )

    # Dias de descanso (pré-jogo OK)
    df[f"rest_days_{side}"] = (
        df.groupby(team_col)["GAME_DATE"]
          .diff()
          .dt.days
    )

    return df

# %%
def add_features_for_all_teams(df):
    df_feat = df_RegularSeason_copy.copy()

    df_feat = generate_team_features_side(df_feat, "HOME")
    df_feat = generate_team_features_side(df_feat, "AWAY")

    # Remover jogos sem histórico suficiente
    df_feat = df_feat[
        df_feat["rolling_pts_5_HOME"].notna() &
        df_feat["rolling_pts_5_AWAY"].notna()
    ].reset_index(drop=True)

    return df_feat


# %%
df_features = add_features_for_all_teams(df_RegularSeason_copy)

# %%
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import xgboost as xgb
import numpy as np

# %%
# %%
# ============================================================
# 1) carregar df_RegularSeason já tratado e com rollings criados
# ============================================================

# Remover jogos sem placar (WL = None significa jogo futuro)
df_train = df_features.dropna(subset=["PTS_HOME", "PTS_AWAY"]).copy()
df_train["TOTAL_PTS"] = df_train["PTS_HOME"].astype(int) + df_train["PTS_AWAY"].astype(int)
df_train["SPREAD"] = df_train["PTS_HOME"].astype(int) - df_train["PTS_AWAY"].astype(int)

# ============================================================
# 2) Selecionar FEATURES (somente numéricas e úteis)
# ============================================================

features = [
    # --- away ---
    'rolling_pts_5_AWAY', 'rolling_plus_minus_5_AWAY',
    'rolling_oreb_7_AWAY', 'rolling_dreb_7_AWAY', 'rolling_ast_7_AWAY',
    'rolling_tov_7_AWAY', 'rolling_fg_pct_10_AWAY',
    'rolling_fg3_pct_10_AWAY', 'rolling_ft_pct_10_AWAY',
    'rest_days_AWAY',

    # --- home ---
    'rolling_pts_5_HOME', 'rolling_plus_minus_5_HOME',
    'rolling_oreb_7_HOME', 'rolling_dreb_7_HOME', 'rolling_ast_7_HOME',
    'rolling_tov_7_HOME', 'rolling_fg_pct_10_HOME',
    'rolling_fg3_pct_10_HOME', 'rolling_ft_pct_10_HOME',
    'rest_days_HOME',
]

X = df_train[features]
y_total = df_train["TOTAL_PTS"]
y_spread = df_train["SPREAD"]
#y = df_train[['PTS_HOME', 'PTS_AWAY']]

# ============================================================
# 3) Train / Test split (SEM embaralhar para manter ordem temporal)
# ============================================================

X_train, X_test, y_total_train, y_total_test = train_test_split(
    X, y_total, test_size=0.15, shuffle=False
)

_, _, y_spread_train, y_spread_test = train_test_split(
    X, y_spread, test_size=0.15, shuffle=False
)

# ============================================================
# 4) Modelo – RANDOM FOREST MULTI-OUTPUT
# ============================================================
model_total = xgb.XGBRegressor(
    n_estimators=600,
    max_depth=4,
    learning_rate=0.01,
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method="hist",
    random_state=42
)

model_spread = xgb.XGBRegressor(
    n_estimators=500,
    max_depth=3,
    learning_rate=0.01,
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method="hist",
    random_state=42
)

# Treinar
model_total.fit(X_train, y_total_train)
model_spread.fit(X_train, y_spread_train)

# Avaliar
total_pred = model_total.predict(X_test)
spread_pred = model_spread.predict(X_test)

pts_home_pred = (total_pred + spread_pred) / 2
pts_away_pred = (total_pred - spread_pred) / 2

pts_home_real = (y_total_test + y_spread_test) / 2
pts_away_real = (y_total_test - y_spread_test) / 2


mae_home = mean_absolute_error(pts_home_real, pts_home_pred)
mae_away = mean_absolute_error(pts_away_real, pts_away_pred)

print("MAE HOME:", mae_home)
print("MAE AWAY:", mae_away)
# ============================================================
# 5) FUNÇÃO PARA PREVER UM JOGO FUTURO
# ============================================================

def prever_jogo(game_id):
    jogo = df_features[df_features["GAME_ID"] == game_id].copy()

    if jogo.empty:
        raise ValueError("GAME_ID não encontrado")

    X_pred = jogo[features]

    total = model_total.predict(X_pred)[0]
    spread = model_spread.predict(X_pred)[0]

    pts_home = (total + spread) / 2
    pts_away = (total - spread) / 2

    # Limites físicos da NBA
    #pts_home = int(np.clip(pts_home, 85, 150))
    #pts_away = int(np.clip(pts_away, 85, 150))

    return {
        "HOME_TEAM": jogo["TEAM_ABBREVIATION_HOME"].iloc[0],
        "AWAY_TEAM": jogo["TEAM_ABBREVIATION_AWAY"].iloc[0],
        "PTS_HOME_PREV": pts_home,
        "PTS_AWAY_PREV": pts_away,
    }

# %%
jogosHoje = df_RegularSeason[(df_RegularSeason['WL_HOME'] != 'W') & (df_RegularSeason['WL_HOME'] != 'L')]['GAME_ID'].unique()
df_hoje = df_RegularSeason[df_RegularSeason['GAME_ID'].isin(jogosHoje)]

# %%
# Garante que as colunas existam
for col in ['PTS_HOME_PREV', 'PTS_AWAY_PREV']:
    if col not in df_RegularSeason.columns:
        df_RegularSeason[col] = np.nan

for jogo in jogosHoje:
    # verifica se o jogo existe nas features
    linha = df_features[df_features['GAME_ID'] == jogo]
    if linha.empty:
        continue

    # NOVA função (não passa mais df_features)
    prev = prever_jogo(jogo)

    if prev is None:
        continue

    df_RegularSeason.loc[
        df_RegularSeason['GAME_ID'] == jogo, 'PTS_HOME_PREV'
    ] = prev['PTS_HOME_PREV']

    df_RegularSeason.loc[
        df_RegularSeason['GAME_ID'] == jogo, 'PTS_AWAY_PREV'
    ] = prev['PTS_AWAY_PREV']

print("Previsao Adicionada")


# %%
df_to_sql = df_RegularSeason[['GAME_ID','GAME_DATE','TEAM_ID_HOME','TEAM_NAME_HOME','PTS_HOME_PREV','TEAM_ID_AWAY','TEAM_NAME_AWAY','PTS_AWAY_PREV']]

# %%
df_to_sql = df_to_sql[df_to_sql['GAME_ID'].isin(jogosHoje)]

# %%
df_to_sql['PTS_HOME_PREV'] = df_to_sql['PTS_HOME_PREV'].round().astype(int)
df_to_sql['PTS_AWAY_PREV'] = df_to_sql['PTS_AWAY_PREV'].round().astype(int)

# %%
import pyodbc
# Conexão com SQL Server
conn = pyodbc.connect('Driver={SQL Server};Server=JUNIOR;Database=NBA;Trusted_Connection=yes;')
cursor = conn.cursor()

# Enviar cada linha do DataFrame
for index, row in df_to_sql.iterrows():
    cursor.execute("EXEC tb_MachineLearning ?,?,?,?,?,?,?,?", 
                row['GAME_ID'], row['GAME_DATE'], row['TEAM_ID_HOME'], row['TEAM_NAME_HOME'], row['PTS_HOME_PREV'], row['TEAM_ID_AWAY'],
                row['TEAM_NAME_AWAY'],row['PTS_AWAY_PREV'])

conn.commit()
conn.close()
print("Dados enviados para o SQL Server!")


