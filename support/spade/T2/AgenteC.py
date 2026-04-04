import asyncio

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message

class AgenteC(Agent):
    class PedidoBehaviour(OneShotBehaviour):
        async def run(self):
            msg = Message(to="agented@mia.lan")
            msg.set_metadata("performative", "request")
            msg.set_metadata("conversation-id", "conv1")
            msg.body = "Executa tarefa X"

            await self.send(msg)
            print("C: Pedido enviado")

            # Esperar confirm
            confirm = await self.receive(timeout=10)
            if confirm:
                print(f"C: Confirm -> {confirm.body}")

            # Esperar inform
            inform = await self.receive(timeout=20)
            if inform:
                print(f"C: Resultado -> {inform.body}")

    async def setup(self):
        print("Agente C remoto iniciado")
        self.add_behaviour(self.PedidoBehaviour())

async def main():
    agente_c = AgenteC("agentec@localhost", "password")

    await agente_c.start()
    print("Ligado?", agente_c.is_alive())

    await asyncio.sleep(20)

    await agente_c.stop()

if __name__ == "__main__":
    asyncio.run(main())