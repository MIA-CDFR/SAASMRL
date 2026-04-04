import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class AgenteB(Agent):
    class ResponderBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                perf = msg.get_metadata("performative")

                if perf == "request":
                    print("B: Recebi pedido")

                    # 1. Confirmar que vai executar
                    confirm = msg.make_reply()
                    confirm.set_metadata("performative", "confirm")
                    confirm.body = "Vou tratar disso!"
                    await self.send(confirm)

                    # Simular processamento
                    await asyncio.sleep(2)

                    # 2. Enviar resultado
                    inform = msg.make_reply()
                    inform.set_metadata("performative", "inform")
                    inform.body = "Tarefa concluída!"
                    await self.send(inform)

    async def setup(self):
        print("Agente B iniciado")
        self.add_behaviour(self.ResponderBehaviour())