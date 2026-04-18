import asyncio
import threading
import jsonpickle
from spade.agent import Agent, Message

class BaseBackgroundAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.agent_loop = asyncio.new_event_loop()

    def _run_loop(self):
        asyncio.set_event_loop(self.agent_loop)
        self.agent_loop.run_forever()

    def start_background(self):
        threading.Thread(target=self._run_loop, daemon=True).start()
        future = asyncio.run_coroutine_threadsafe(self.start(), self.agent_loop)
        future.result()
        print(f"[{self.__class__.__name__}] {self.jid} iniciado em background")

    def stop_background(self):
        future = asyncio.run_coroutine_threadsafe(self.stop(), self.agent_loop)
        future.result()
        self.agent_loop.call_soon_threadsafe(self.agent_loop.stop)
        print(f"[{self.__class__.__name__}] {self.jid} parado")

    async def forward_message(
        self,
        behaviour,
        payload,
        agent_to,
        performative,
        ontology,
        conversation_id
    ):
        msg = Message(to=agent_to)
        msg.set_metadata("performative", performative)
        msg.set_metadata("ontology", ontology)
        msg.set_metadata("conversation-id", conversation_id)

        payload_copy = payload.copy()

        payload_copy.setdefault("visited_agents", [])

        current_agent = str(self.jid)

        if current_agent not in payload_copy["visited_agents"]:
            payload_copy["visited_agents"].append(current_agent)

        msg.body = jsonpickle.encode(payload_copy)

        await behaviour.send(msg)

        print(f"[{self.__class__.__name__}] Mensagem enviada para {agent_to}")