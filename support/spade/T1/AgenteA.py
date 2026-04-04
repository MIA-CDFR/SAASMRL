import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.template import Template
from spade.message import Message

class AgenteA(Agent):
    class PedidoBehaviour(OneShotBehaviour):
        async def run(self):
            # Enviar pedido
            msg = Message(to="agenteb@localhost")
            msg.set_metadata("performative", "request")
            msg.body = "Executa tarefa X"

            await self.send(msg)
            print("A: Pedido enviado")

            # Esperar confirm
            confirm = await self.receive(timeout=5)
            if confirm and confirm.get_metadata("performative") == "confirm":
                print(f"A: Confirm recebido -> {confirm.body}")

            # Esperar resultado
            inform = await self.receive(timeout=10)
            if inform and inform.get_metadata("performative") == "inform":
                print(f"A: Resultado -> {inform.body}")

    async def setup(self):
        print("Agente A iniciado")

        # Template para receber apenas confirm/inform (opcional mas recomendado)
        template = Template()
        self.add_behaviour(self.PedidoBehaviour(), template)