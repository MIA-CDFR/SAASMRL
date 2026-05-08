import asyncio
import threading
import uuid
import jsonpickle

from spade.agent import Agent
from spade.message import Message
from spade.behaviour import OneShotBehaviour

# Exemplo de implementação de um agente base para enviar mensagens a outros agentes, como o SensorAgent
# sender_agent = BaseSenderAgent(
#     "api_agent@localhost",
#     "password"
# )

# def start_api():
#     sender_agent.start_background()
#     app.run(host="0.0.0.0", port=5000, debug=True)


# def stop_api():
#     sender_agent.stop_background()

#         future = asyncio.run_coroutine_threadsafe(
#             sender_agent.send_message(
#                 payload=data,
#                 agent_to="sensor_agent@localhost",
#                 performative="inform",
#                 ontology="sensor_activity"
#             ),
#             sender_agent.agent_loop
#         )

class SendMessageBehaviour(OneShotBehaviour):
    def __init__(
        self,
        payload: dict,
        agent_to: str,
        performative: str,
        ontology: str
    ):
        super().__init__()
        self.payload = payload
        self.agent_to = agent_to
        self.performative = performative
        self.ontology = ontology

    async def run(self):
        msg = Message(to=self.agent_to)
        msg.set_metadata("performative", self.performative)
        msg.set_metadata("ontology", self.ontology)
        msg.set_metadata("conversation-id", f"conv-{self.agent.jid}-guid-{uuid.uuid4()}")

        payload = self.payload.copy()

        payload.setdefault("visited_agents", [])
        payload["visited_agents"].append(str(self.agent.jid))

        msg.body = jsonpickle.encode(payload)
    
        await self.send(msg)

        #print(f"Mensagem enviada para {self.agent_to}")
        #print(f"Payload: {self.payload}")
        #print(f"Performative: {self.performative}")
        #print(f"Ontology: {self.ontology}")


class BaseSenderAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.agent_loop = asyncio.new_event_loop()

    def run_loop(self):
        asyncio.set_event_loop(self.agent_loop)
        self.agent_loop.run_forever()

    def start_background(self):
        threading.Thread(
            target=self.run_loop,
            daemon=True
        ).start()

        future = asyncio.run_coroutine_threadsafe(
            self.start(),
            self.agent_loop
        )

        future.result()
        #print(f"{self.jid} iniciado")

    def stop_background(self):
        future = asyncio.run_coroutine_threadsafe(
            self.stop(),
            self.agent_loop
        )

        future.result()
        self.agent_loop.call_soon_threadsafe(self.agent_loop.stop)

        #print(f"{self.jid} parado")

    # async def send_message(
    #     self,
    #     payload: dict,
    #     agent_to: str,
    #     performative: str,
    #     ontology: str
    # ):
    #     behaviour = SendMessageBehaviour(
    #         payload=payload,
    #         agent_to=agent_to,
    #         performative=performative,
    #         ontology=ontology
    #     )

    #     self.add_behaviour(behaviour)
    async def send_message(
        self,
        payload: dict,
        agent_to: str,
        performative: str,
        ontology: str
    ):
        behaviour = SendMessageBehaviour(
            payload=payload,
            agent_to=agent_to,
            performative=performative,
            ontology=ontology
        )

        self.add_behaviour(behaviour)

        await behaviour.join()        
