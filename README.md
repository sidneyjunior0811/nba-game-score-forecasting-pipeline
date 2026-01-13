# nba-game-score-forecasting-pipeline
end-to-end data pipeline for forecasting NBA game scores using historical data, automated ingestion, and season-phase modeling

**Objetivo:** Desenvolver uma solução analítica end-to-end para estimar placares esperados e padrões de pontuação de jogos futuros da NBA, integrando dados de múltiplas fontes, realizando tratamento e análise estatística, e disponibilizando os resultados em um dashboard interativo.

### **Fluxo do Projeto:**
  **Fontes de Dados --> Armazenamento e Tratamento de Dados --> Análise e Modelagem --> Visualização e Entrega**

### Passo 01️ - Fontes de Dados (Data Sources)

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

### Passo 02 - Armazenamento e Tratamento de Dados (Data Engineering)

* **ELT (Extract, Load, Transform)**
  - Criação de tabelas no banco de dados
  - Persistência dos dados coletados via Web Scraping e APIs
  - Armazenamento de dados brutos (raw layer)
  
* **ETL (Extract, Transform, Load)**
  - Padronização de formatos e campos
  - Limpeza de dados inconsistentes ou faltantes
  - Integração entre múltiplas fontes
  - Geração de tabelas tratadas e consolidadas (trusted / curated layer)

### Passo 03 - Análise e Modelagem (Analytics & Forecast)

* **Análise estatística de desempenho dos times**
  - Criação de métricas analíticas
  - Uso de dados históricos para:
      - Identificação de padrões
      - Previsão dos resultados e placares de jogos futuros

### Passo 04 - Visualização e Entrega (Dashboard)

* **Dashboard interativo com:**
  - Jogos do dia
  - Placar e status das partidas
  - Logos dos times
  - Classificação atualizada da liga
  - Estatísticas relevantes
  - Previsões de jogos futuros

### Passo 05 - Resultado Final

  - **Pipeline de dados end-to-end**
  - **Integração de múltiplas fontes oficiais e não oficiais**
  - **Suporte à análise esportiva e tomada de decisão**
  - **Estrutura escalável para novas métricas, temporadas e modelos**


### Limitações do Projeto

* **Dependência da atualização das APIs:**
    - As APIs utilizadas não possuem documentação oficial sobre a frequência de atualização dos dados.
    - A partir de análises empíricas, foi identificado que as informações são atualizadas principalmente próximo ao início das partidas ou durante jogos em andamento.

* **Latência na disponibilidade dos dados:**
    - Em alguns cenários, pode haver atraso na atualização de placares, status das partidas ou estatísticas, impactando a atualização em tempo quase real do dashboard.

* **Estratégia de agendamento (Scheduling):**
  - Para mitigar essa limitação, o pipeline foi agendado para:
    - Iniciar às 19h
    - Executar atualizações a cada 30 minutos

**Essa abordagem garante maior sincronização com os horários das partidas e melhora a confiabilidade das informações exibidas**
