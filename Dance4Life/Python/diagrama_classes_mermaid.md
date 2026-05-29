# Diagrama de Classes - Dance4Life Agent Architecture

## Código Mermaid

```mermaid
classDiagram
    Agent <|-- BaseBackgroundAgent
    BaseBackgroundAgent <|-- BaseSenderAgent
    BaseBackgroundAgent <|-- SensorAgent
    BaseBackgroundAgent <|-- CoordinatorAgent
    BaseBackgroundAgent <|-- HarAgent
    BaseBackgroundAgent <|-- EnvironmentAgent
    BaseBackgroundAgent <|-- DatabaseAgent
    BaseBackgroundAgent <|-- MatchingAgent
    BaseBackgroundAgent <|-- ClusteringAgent
    
    OneShotBehaviour <|-- SendMessageBehaviour
    CyclicBehaviour <|-- ReceiveSensorDataBehaviour
    CyclicBehaviour <|-- ReceiveCoordinatorDataBehaviour
    CyclicBehaviour <|-- ReceiveHarDataBehaviour
    CyclicBehaviour <|-- EnvironmentDataBehaviour
    CyclicBehaviour <|-- ReceiveDatabaseDataBehaviour
    CyclicBehaviour <|-- ReceiveMatchingDataBehaviour
    
    SensorAgent *-- ReceiveSensorDataBehaviour
    CoordinatorAgent *-- ReceiveCoordinatorDataBehaviour
    HarAgent *-- ReceiveHarDataBehaviour
    EnvironmentAgent *-- EnvironmentDataBehaviour
    DatabaseAgent *-- ReceiveDatabaseDataBehaviour
    MatchingAgent *-- ReceiveMatchingDataBehaviour
    
    UserActivityClusterModel .. ClusteringAgent
    
    class Agent{
        <<SPADE_Framework>>
        +start()
        +stop()
    }
    
    class BaseBackgroundAgent{
        -agent_loop: asyncio.AbstractEventLoop
        -__init__(jid, password)
        +_run_loop()
        +start_background()
        +stop_background()
        +_run_unregister()
        +forward_message()
    }
    
    class BaseSenderAgent{
        <<Auxiliary>>
        +send_message()
    }
    
    class OneShotBehaviour{
        <<SPADE_Framework>>
        +run()
    }
    
    class CyclicBehaviour{
        <<SPADE_Framework>>
        +run()
    }
    
    class SendMessageBehaviour{
        -payload: dict
        -agent_to: str
        -performative: str
        -ontology: str
        +run()
    }
    
    class SensorAgent{
        <<Agent_Role>>
        +setup()
    }
    
    class ReceiveSensorDataBehaviour{
        +run()
        --Forward to COORDINATOR_AGENT
    }
    
    class CoordinatorAgent{
        <<Agent_Role>>
        +setup()
    }
    
    class ReceiveCoordinatorDataBehaviour{
        +run()
        --Forward to HAR_AGENT
        --Forward to DATABASE_AGENT
    }
    
    class HarAgent{
        <<Agent_Role>>
        +setup()
    }
    
    class ReceiveHarDataBehaviour{
        +run()
        --Forward to ENVIRONMENT_AGENT
        --Forward to MATCHING_AGENT
    }
    
    class EnvironmentAgent{
        <<Agent_Role>>
        +setup()
    }
    
    class EnvironmentDataBehaviour{
        +run()
        --Enrich payload com weather
        --Forward to DATABASE_AGENT
    }
    
    class DatabaseAgent{
        <<Agent_Role>>
        +setup()
    }
    
    class ReceiveDatabaseDataBehaviour{
        +run()
        --save_activity()
        --save_matching()
        --save_movement_recommendation()
    }
    
    class MatchingAgent{
        <<Agent_Role>>
        +setup()
    }
    
    class ReceiveMatchingDataBehaviour{
        +run()
        --Process user matching
    }
    
    class ClusteringAgent{
        <<Agent_Role>>
        -cluster_model: UserActivityClusterModel
        +__init__(jid, password)
        +_notify_cluster_invite()
    }
    
    class UserActivityClusterModel{
        <<Data_Model>>
        +fit()
        +predict()
    }
```

## Fluxo de Dados

```
SensorAgent 
    ↓ (forward_message)
CoordinatorAgent 
    ↓↓
HarAgent ← EnvironmentAgent
    ↓↓
MatchingAgent → ClusteringAgent
    ↓
DatabaseAgent (Firebase)
```

## Descrição dos Componentes

### Agentes Principais

| Agente | Responsabilidade |
|--------|-----------------|
| **SensorAgent** | Ponto de entrada para dados de sensores externos |
| **CoordinatorAgent** | Orquestra o fluxo de mensagens entre agentes |
| **HarAgent** | Processa Human Activity Recognition (HAR) |
| **EnvironmentAgent** | Enriquece dados com informações ambientais (weather) |
| **DatabaseAgent** | Persiste dados em Firebase |
| **MatchingAgent** | Processa matching entre usuários |
| **ClusteringAgent** | Realiza clustering de atividades de usuários |

### Comportamentos

- **ReceiveSensorDataBehaviour**: Recebe e processa dados de sensores
- **ReceiveCoordinatorDataBehaviour**: Coordena fluxo de mensagens
- **ReceiveHarDataBehaviour**: Processa HAR e encaminha para múltiplos agentes
- **EnvironmentDataBehaviour**: Enriquece payload com dados ambientais
- **ReceiveDatabaseDataBehaviour**: Salva dados em Firebase
- **ReceiveMatchingDataBehaviour**: Processa matching de usuários

### Base Classes

- **BaseBackgroundAgent**: Gerencia execução assíncrona em thread separada
- **BaseSenderAgent**: Auxiliar para envio de mensagens

### Modelos de Dados

- **UserActivityClusterModel**: Modelo de clustering de atividades de usuários
