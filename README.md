# nba-game-score-forecasting-pipeline
end-to-end data pipeline for forecasting NBA game scores using historical data, automated ingestion, and season-phase modeling

Objetivo: Desenvolver uma solução analítica end-to-end para prever os placares dos jogos futuros da NBA, integrando dados de múltiplas fontes, realizando tratamento e análise estatística, e disponibilizando os resultados em um dashboard interativo.

1️⃣ Fontes de Dados (Data Sources)

* **Web Scraping**
  - Resultados das partidas
  - Links dos jogos
  - Logos dos times
  - Status da partida (pré-jogo, em andamento, finalizada)

* **API – Classificação da Liga**
  - Posição dos times
  - Vitórias, derrotas
  - Desempenho geral na temporada
  - API – Jogos do Dia
  - Partidas programadas para o dia
  - Status da partida
  - Data e horário do jogo

* **API – Histórico por Temporada (Season)**
  - Estatísticas históricas dos jogos
  - Dados individuais e coletivos
  - Base para desenvolvimento de modelos de previsão de placar

2️⃣ Armazenamento e Tratamento de Dados (Data Engineering)

* **ELT (Extract, Load, Transform)**
  - Criação de tabelas no banco de dados
  - Persistência dos dados coletados via Web Scraping e APIs
  - Armazenamento de dados brutos (raw layer)

* **ETL (Extract, Transform, Load)**
  - Padronização de formatos e campos
  - Limpeza de dados inconsistentes ou faltantes
  - Integração entre múltiplas fontes
  - Geração de tabelas tratadas e consolidadas (trusted / curated layer)

3️⃣ Análise e Modelagem (Analytics & Forecast)

* **Análise estatística de desempenho dos times**
  - Criação de métricas analíticas
  - Uso de dados históricos para:
      - Identificação de padrões
      - Previsão dos resultados e placares de jogos futuros

4️⃣ Visualização e Entrega (Dashboard)

* **Dashboard interativo com:**
  - Jogos do dia
  - Placar e status das partidas
  - Logos dos times
  - Classificação atualizada da liga
  - Estatísticas relevantes
  - Previsões de jogos futuros

5️⃣ Resultado Final

  - **Pipeline de dados end-to-end**
  - **Integração de múltiplas fontes oficiais e não oficiais**
  - **Suporte à análise esportiva e tomada de decisão**
  - **Estrutura escalável para novas métricas, temporadas e modelos**
    
