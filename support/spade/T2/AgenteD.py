import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

class AgenteD(Agent):
    class ResponderBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                perf = msg.get_metadata("performative")
                print(f"D: Recebeu de {msg.sender}")

                if perf == "request":
                    print(f"D: Pedido recebido de {msg.sender}")

                    # Confirmar
                    confirm = msg.make_reply()
                    confirm.set_metadata("performative", "confirm")
                    confirm.body = "Vou tratar disso!"
                    await self.send(confirm)

                    await asyncio.sleep(2)

                    # Resultado
                    inform = msg.make_reply()
                    inform.set_metadata("performative", "inform")
                    inform.body = "Tarefa concluída!"
                    await self.send(inform)

    async def setup(self):
        print("Agente D remoto iniciado")
        self.add_behaviour(self.ResponderBehaviour())

async def main():
    agente_d = AgenteD("agented@localhost", "password")

    await agente_d.start()
    print("Ligado?", agente_d.is_alive())

    await asyncio.sleep(999999)


if __name__ == "__main__":
    asyncio.run(main())