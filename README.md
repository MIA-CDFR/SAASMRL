# Dance4Life

**Universidade do Minho — Mestrado em Inteligência Artificial**

Dance4Life é uma plataforma integrada de promoção do envelhecimento ativo através da dança. Combina sensorização vestível, agentes inteligentes, visualização de dados e aprendizagem por reforço para personalizar o acompanhamento de atividade física de utilizadores mais velhos em tempo real.

---

## Equipa

| Aluno    | Nome                                    |
|----------|-----------------------------------------|
| PG11605  | Carlos da Mota Bergueira                |
| PG59999  | Diego Jefferson Mendes Silva            |
| PG42201  | Filipa Araújo Pereira                   |
| PG7942   | Rui Manuel Martins Marques Rodrigues    |

---

## Estrutura do Projeto

```
Dance4Life/
├── AndroidSensor/   ← Sensorização e Ambiente
├── Python/          ← Agentes e Sistemas Multi-Agente
├── D3_web/          ← Visualização de Dados e Conhecimento
└── RL/              ← Aprendizagem por Reforço
support/
└── SVDC/            ← Dashboard Power BI (Visualização de Dados)
```

---

## Unidades Curriculares

### Sensorização e Ambiente — `Dance4Life/AndroidSensor`

Aplicação Android (Kotlin, API 35) que recolhe dados de sensores do smartphone e de um dispositivo Wear OS emparelhado:

- **Acelerómetro e giroscópio** — cálculo de magnitudes de movimento em tempo real
- **Frequência cardíaca** — leitura via sensor ótico (smartphone e Wear OS)
- **Localização GPS** — latitude, longitude e cidade atual
- **RitmoCalculator** — janela deslizante de 1 minuto que produz uma pontuação escalar de *ritmo* representando a intensidade do movimento
- **DanceController** — orquestra toda a pipeline de sensores, inferência RL e envio de dados para o backend
- Os dados são enviados periodicamente para o backend Python via API REST

A aplicação inclui também um módulo Wear OS que sincroniza dados de frequência cardíaca com o smartphone via `DataClient`.

---

### Agentes e Sistemas Multi-Agente — `Dance4Life/Python`

Backend multi-agente implementado com a framework **SPADE** e uma API REST **Flask**. Cada preocupação lógica é atribuída a um agente dedicado:

| Agente              | Responsabilidade                                                                 |
|---------------------|----------------------------------------------------------------------------------|
| `SensorAgent`       | Recebe payloads de sensores da app Android e reencaminha para o CoordinatorAgent |
| `CoordinatorAgent`  | Hub de roteamento — despacha para HarAgent e ClusteringAgent                    |
| `HarAgent`          | Reconhecimento de atividade humana; reencaminha para EnvironmentAgent            |
| `EnvironmentAgent`  | Enriquece o payload com dados meteorológicos (temperatura) e reencaminha         |
| `DatabaseAgent`     | Persiste os dados enriquecidos no Firebase Realtime Database                     |
| `ClusteringAgent`   | Agrupamento de utilizadores por k-médias com base no *ritmo*; gera convites de progressão de nível (*Iniciante → Moderado → Avançado → Expert*) |

A API Flask expõe endpoints para registo de agentes, heartbeat, recolha de atividade, matching de utilizadores e consulta de dados, servindo também o painel web estático na porta 8000.

---

### Visualização de Dados e Conhecimento — `Dance4Life/D3_web` e `support/SVDC`

**`Dance4Life/D3_web`** — Painel web interativo em HTML/CSS/JavaScript com ligação direta ao Firebase:

- Visualizações em tempo real de atividade, recomendações de movimento e agrupamentos de utilizadores
- Gráficos de evolução de *ritmo*, distribuição de clusters e histórico de convites
- Datasets sintéticos CSV (`dance4life_activity.csv`, `dance4life_matching.csv`, etc.) para desenvolvimento e testes

**`support/SVDC`** — Dashboard em **Power BI** (`dashboard_CB_v3.pbix`) com análise exploratória dos dados recolhidos, incluindo tendências de atividade, distribuição de clusters e padrões de utilização.

---

### Aprendizagem por Reforço — `Dance4Life/RL`

Pipeline completo de treino, avaliação e exportação de uma política de acompanhamento por Aprendizagem por Reforço:

#### Ambiente (`RL/training/src/env/movement_env.py`)
Ambiente Gymnasium personalizado que modela o estado do utilizador como um vetor tridimensional contínuo em $[0, 10]^3$:

| Dimensão            | Descrição                              |
|---------------------|----------------------------------------|
| `activity_level`    | Nível atual de movimento               |
| `physical_fatigue`  | Fadiga fisiológica acumulada           |
| `irritation_level`  | Fadiga de alarmes causada por intervenções |

**Ações:** silêncio (0), intensidade baixa (1), média (2), alta (3)  
**Recompensa:** +15 na zona saudável, −5 se sedentário, −50 e terminação se fadiga ou irritação ≥ 10  
**Episódio:** 96 passos (dia simulado de decisões de acompanhamento)

#### Algoritmos (`RL/training/`)
PPO e DQN treinados com Stable-Baselines3 durante 400 000 passos:

| Algoritmo | Recompensa Média | Desvio Padrão | Taxa de Sobrevivência |
|-----------|-----------------|---------------|----------------------|
| PPO       | 1 434,5         | ± 2,1         | 100%                 |
| DQN       | 1 432,8         | ± 4,3         | 100%                 |

Ambos atingem ~99,7% da recompensa máxima teórica (1 440), com 100% de taxa de sobrevivência após convergência em ~50 000 passos.

#### Exportação e Integração Android (`RL/export/`)
A melhor política PPO é exportada para **ONNX** (`dance4life_coach_v2_ppo.onnx`) e copiada para `AndroidSensor/app/src/main/assets/models/`. O módulo `OnnxRlCoachPolicy` (Kotlin) carrega o modelo via ONNX Runtime e realiza inferência em tempo real a partir dos sensores do dispositivo.

---

## Como Executar

### Backend Python
```bash
cd Dance4Life/Python
uv sync          # instalar dependências
python main.py   # inicia agentes SPADE + API Flask na porta 5000
                 # painel web disponível em http://localhost:8000/dashboard.html
```

### Treino RL
```bash
cd Dance4Life/RL/training
uv sync
python src/train.py --algo both   # treina PPO e DQN
python src/evaluate.py --algo compare --episodes 20
```

### Aplicação Android
Usar as tarefas VS Code configuradas em `.vscode/tasks.json` ou:
```bash
cd Dance4Life/AndroidSensor
./gradlew assembleDebug
```

