# Dance4Life Reinforcement Learning Coach

## Overview

Este projeto implementa um sistema de **Reinforcement Learning (RL)** para o ecossistema Dance4Life, permitindo treinar agentes inteligentes capazes de adaptar intervenções de coaching com o objetivo de aumentar a atividade física dos utilizadores sem provocar níveis excessivos de fadiga ou irritação.

O projeto suporta dois algoritmos de Reinforcement Learning:

* **PPO (Proximal Policy Optimization)**
* **DQN (Deep Q-Network)**

Após o treino, os modelos podem ser exportados para **ONNX** e integrados diretamente na aplicação Android para inferência local.

---

# Reinforcement Learning Concepts

O Reinforcement Learning é uma área de Machine Learning onde um agente aprende a tomar decisões através da interação com um ambiente.

O objetivo é maximizar a recompensa acumulada ao longo do tempo através de tentativa e erro.

## Agente (Agent)

O agente é a entidade responsável por tomar decisões e executar ações.

No Dance4Life, o agente representa o sistema de coaching inteligente que decide qual o nível de intervenção mais adequado para o utilizador.

---

## Ambiente (Environment)

O ambiente representa o mundo onde o agente opera.

Sempre que o agente executa uma ação, o ambiente responde alterando o seu estado e devolvendo uma recompensa.

No Dance4Life, o ambiente simula o comportamento de um utilizador ao longo do tempo.

---

## Estado (State)

O estado representa a situação atual observada pelo agente.

É a informação utilizada para decidir qual a próxima ação.

O estado do ambiente é representado por:

```text
[activity_level, physical_fatigue, irritation_level]
```

Exemplo:

```text
[6, 2, 1]
```

onde:

* activity_level = 6
* physical_fatigue = 2
* irritation_level = 1

---

## Ação (Action)

Uma ação corresponde a uma decisão tomada pelo agente.

Após observar o estado atual, o agente escolhe uma ação que considera mais vantajosa.

---

## Recompensa (Reward)

A recompensa é o feedback fornecido pelo ambiente após a execução de uma ação.

O objetivo do treino é maximizar a soma das recompensas recebidas ao longo do tempo.

A recompensa funciona como um mecanismo de aprendizagem que orienta o agente para comportamentos desejáveis.

---

## Ciclo de Aprendizagem

O processo de Reinforcement Learning segue continuamente os seguintes passos:

```text
Estado Atual
      │
      ▼
   Agente
      │
      ▼
    Ação
      │
      ▼
 Ambiente
      │
      ▼
Novo Estado + Recompensa
      │
      └───────────────┐
                      ▼
                 Agente
```

Ao repetir este ciclo milhares de vezes durante o treino, o agente aprende quais as ações que produzem melhores resultados em cada situação.

---

# Environment Design

## State Space

O ambiente é definido através de três variáveis observáveis:

| Variável         | Intervalo |
| ---------------- | --------- |
| activity_level   | 0 – 10    |
| physical_fatigue | 0 – 10    |
| irritation_level | 0 – 10    |

Input do modelo:

```text
[activity_level, physical_fatigue, irritation_level]
```

---

## Action Space

O agente pode escolher uma das seguintes ações:

| Action ID | Descrição       |
| --------- | --------------- |
| 0         | Silence         |
| 1         | Low Coaching    |
| 2         | Medium Coaching |
| 3         | High Coaching   |

Estas ações representam diferentes níveis de intervenção do sistema de coaching.

---

## Reward Function

O ambiente recompensa estados considerados saudáveis.

### Recompensa Positiva

```text
+15
```

quando:

```text
activity_level ∈ [4,7]
physical_fatigue < 7
irritation_level < 5
```

### Penalização por Baixa Atividade

```text
-5
```

quando:

```text
activity_level < 2
```

### Penalização por Estado Crítico

```text
-50
```

e fim do episódio quando:

```text
physical_fatigue >= 10
```

ou

```text
irritation_level >= 10
```

---

# Supported Algorithms

## PPO (Proximal Policy Optimization)

O PPO é um algoritmo baseado em **Policy Gradient**.

Em vez de aprender diretamente o valor de cada ação, aprende uma política que produz probabilidades para cada ação disponível.

### Vantagens

* Treino estável
* Boa capacidade de generalização
* Menor sensibilidade a hiperparâmetros
* Excelente desempenho em ambientes complexos

### Funcionamento

1. O agente interage com o ambiente.
2. São recolhidas trajetórias de experiência.
3. É calculada a vantagem (Advantage Estimate).
4. A política é atualizada através de clipping.
5. O processo repete-se até convergência.

### Quando Utilizar PPO

Recomendado quando:

* Se pretende maior estabilidade de treino.
* Existe maior complexidade no ambiente.
* A robustez é mais importante do que a velocidade de treino.

---

## DQN (Deep Q-Network)

O DQN é um algoritmo baseado em **Value Functions**.

Aprende uma função:

```text
Q(state, action)
```

que estima a recompensa futura esperada para cada ação.

### Vantagens

* Simples de interpretar
* Muito eficaz para ações discretas
* Treino rápido

### Funcionamento

1. O agente observa um estado.
2. A rede calcula os valores Q para cada ação.
3. É escolhida a ação com maior valor esperado.
4. A experiência é armazenada num Replay Buffer.
5. O treino é realizado através de amostragem aleatória desse buffer.

### Quando Utilizar DQN

Recomendado quando:

* O espaço de ações é pequeno e discreto.
* É desejado um treino mais rápido.
* A interpretabilidade é importante.

---

# Training Configuration

Todos os hiperparâmetros de treino encontram-se definidos em:

```text
training/config/training_config.yaml
```

---

## PPO Configuration

```yaml
ppo:
  learning_rate: 0.0003
  n_steps: 1024
  batch_size: 64
  n_epochs: 10
  gamma: 0.99
  gae_lambda: 0.95
  clip_range: 0.2
  ent_coef: 0.01
  vf_coef: 0.5
  max_grad_norm: 0.5
```

| Parâmetro     | Descrição                              |
| ------------- | -------------------------------------- |
| learning_rate | Taxa de aprendizagem                   |
| n_steps       | Passos recolhidos antes da atualização |
| batch_size    | Tamanho do mini-batch                  |
| n_epochs      | Número de épocas                       |
| gamma         | Discount factor                        |
| gae_lambda    | Generalized Advantage Estimation       |
| clip_range    | Limite de clipping PPO                 |
| ent_coef      | Incentivo à exploração                 |
| vf_coef       | Peso da Value Function                 |
| max_grad_norm | Gradient clipping                      |

---

## DQN Configuration

```yaml
dqn:
  learning_rate: 0.0005
  buffer_size: 100000
  learning_starts: 5000
  batch_size: 128
  tau: 1.0
  gamma: 0.99
  train_freq: 4
  gradient_steps: 1
  target_update_interval: 1000
  exploration_fraction: 0.25
  exploration_initial_eps: 1.0
  exploration_final_eps: 0.05
  max_grad_norm: 10.0
```

| Parâmetro               | Descrição                      |
| ----------------------- | ------------------------------ |
| buffer_size             | Replay Buffer Size             |
| learning_starts         | Passos antes de iniciar treino |
| batch_size              | Tamanho do batch               |
| tau                     | Soft Update Factor             |
| gamma                   | Discount Factor                |
| train_freq              | Frequência de treino           |
| gradient_steps          | Atualizações por ciclo         |
| target_update_interval  | Atualização da Target Network  |
| exploration_fraction    | Percentagem de exploração      |
| exploration_initial_eps | Epsilon inicial                |
| exploration_final_eps   | Epsilon final                  |
| max_grad_norm           | Gradient clipping              |

---

## Global Training Parameters

```yaml
training:
  total_timesteps: 400000
  n_envs: 8
  eval_freq: 10000
  n_eval_episodes: 20
  seed: 42
  episode_length: 96
```

| Parâmetro       | Descrição                  |
| --------------- | -------------------------- |
| total_timesteps | Número total de interações |
| n_envs          | Ambientes paralelos        |
| eval_freq       | Frequência de avaliação    |
| n_eval_episodes | Episódios de avaliação     |
| seed            | Seed de reprodutibilidade  |
| episode_length  | Duração máxima do episódio |

---

# Training

## Train PPO

```bash
python src/train.py --algo ppo
```

---

## Train DQN

```bash
python src/train.py --algo dqn
```

---

## Train Both

```bash
python src/train.py --config config/training_config.yaml --algo both
```

---

## Training Outputs

Os modelos treinados são armazenados em:

```text
training/checkpoints/
```

Normalmente incluem:

```text
best_model.zip
final_model.zip
evaluation_logs/
tensorboard/
```

---

# Evaluation

Comparação entre PPO e DQN:

```bash
python src/evaluate.py --algo compare --episodes 20
```

Avaliação individual:

```bash
python src/evaluate.py --algo ppo --model checkpoints/ppo/best/best_model

python src/evaluate.py --algo dqn --model checkpoints/dqn/best/best_model
```

Métricas avaliadas:

* Mean Reward
* Episode Length
* Survival Rate
* Policy Stability

---

# ONNX Export

Após o treino, os modelos Stable-Baselines3 devem ser convertidos para ONNX para utilização na aplicação Android.

Script responsável:

```text
export/export_onnx.py
```

---

## O que faz o export_onnx.py

O script:

1. Carrega um modelo PPO ou DQN treinado.
2. Extrai a rede de inferência.
3. Converte a rede para ONNX.
4. Gera um ficheiro compatível com ONNX Runtime.
5. Opcionalmente valida o modelo exportado.

O objetivo é remover a dependência de Python e Stable-Baselines3 em ambiente mobile.

---

## Export PPO

```bash
python export/export_onnx.py \
  --algo ppo \
  --model checkpoints/ppo/best/best_model \
  --validate
```

---

## Export DQN

```bash
python export/export_onnx.py \
  --algo dqn \
  --model checkpoints/dqn/best/best_model \
  --validate
```

---

## Validation

Quando utilizada a flag:

```bash
--validate
```

o script executa inferência utilizando ONNX Runtime para garantir que o modelo exportado produz resultados válidos.

---

## ONNX Inputs

```text
[activity_level, physical_fatigue, irritation_level]
```

---

## ONNX Outputs

```text
[action_scores]
```

Correspondentes a:

```text
0 = Silence
1 = Low Coaching
2 = Medium Coaching
3 = High Coaching
```

---

# Android Integration

Após a exportação, o ficheiro ONNX deve ser copiado manualmente para:

```text
Dance4Life\AndroidSensor\core\src\main\java\com\dance4life\core\data\rl
```

Exemplo:

```text
dance4life_coach_v2_ppo.onnx
```

ou

```text
dance4life_coach_v2_dqn.onnx
```

A aplicação Android utiliza este modelo para executar inferência local através de ONNX Runtime, sem necessidade de Python ou Stable-Baselines3.

---

# End-to-End Pipeline

```text
┌────────────────────────────┐
│ training_config.yaml       │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Train PPO / DQN            │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Model Checkpoints          │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Evaluate Models            │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Select Best Model          │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ export_onnx.py             │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ *.onnx                     │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Copy ONNX to Android       │
│ core/data/rl              │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Android Inference          │
└────────────────────────────┘
```

---

# Technology Stack

* Python 3.x
* Stable-Baselines3
* PyTorch
* Gymnasium
* ONNX
* ONNX Runtime
* Android
* Kotlin
* ONNX Runtime Mobile
