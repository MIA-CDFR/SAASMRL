import asyncio
import threading
import jsonpickle
import requests

from spade.agent import Agent, Message
from spade.behaviour import OneShotBehaviour, PeriodicBehaviour
from config.config import SeververConfig

SERVER_URL = f"http://{SeververConfig.SERVER_HOSTNAME}:{SeververConfig.SERVER_PORT}"


class BaseBackgroundAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.agent_loop = asyncio.new_event_loop()

    # ---------------------------
    # LOOP BACKGROUND
    # ---------------------------
    def _run_loop(self):
        asyncio.set_event_loop(self.agent_loop)
        self.agent_loop.run_forever()

    def start_background(self):
        threading.Thread(target=self._run_loop, daemon=True).start()

        future = asyncio.run_coroutine_threadsafe(
            self.start(),
            self.agent_loop
        )
        future.result()

        print(f"[{self.__class__.__name__}] {self.jid} iniciado em background")

    def stop_background(self):
        # unregister antes de parar
        future = asyncio.run_coroutine_threadsafe(
            self._run_unregister(),
            self.agent_loop
        )
        future.result()

        future = asyncio.run_coroutine_threadsafe(
            self.stop(),
            self.agent_loop
        )
        future.result()

        self.agent_loop.call_soon_threadsafe(self.agent_loop.stop)

        print(f"[{self.__class__.__name__}] {self.jid} parado")

    # ---------------------------
    # REGISTER
    # ---------------------------
    class RegisterBehaviour(OneShotBehaviour):
        async def run(self):
            try:
                requests.post(f"{SERVER_URL}/register_agent", json={
                    "jid": str(self.agent.jid)
                })
                print(f"[{self.agent.jid}] registado no server")
            except Exception as e:
                print(f"[REGISTER ERROR] {e}")

    # ---------------------------
    # HEARTBEAT
    # ---------------------------
    class HeartbeatBehaviour(PeriodicBehaviour):
        async def run(self):
            try:
                requests.post(f"{SERVER_URL}/heartbeat", json={
                    "jid": str(self.agent.jid)
                })
                print(f"[{self.agent.jid}] heartbeat enviado")
            except Exception as e:
                print(f"[HEARTBEAT ERROR] {e}")

    # ---------------------------
    # UNREGISTER
    # ---------------------------
    class UnregisterBehaviour(OneShotBehaviour):
        async def run(self):
            try:
                requests.post(f"{SERVER_URL}/unregister_agent", json={
                    "jid": str(self.agent.jid)
                })
                print(f"[{self.agent.jid}] removido do server")
            except Exception as e:
                print(f"[UNREGISTER ERROR] {e}")

    async def _run_unregister(self):
        behaviour = self.UnregisterBehaviour()
        self.add_behaviour(behaviour)
        await behaviour.join()

    # ---------------------------
    # SETUP BASE
    # ---------------------------
    async def setup(self):
        print(f"[{self.__class__.__name__}] setup base")

        # register uma vez
        self.add_behaviour(self.RegisterBehaviour())

        # heartbeat loop
        heartbeat = self.HeartbeatBehaviour(period=10)
        self.add_behaviour(heartbeat)

    # ---------------------------
    # FORWARD MESSAGE
    # ---------------------------
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