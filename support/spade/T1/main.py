import asyncio

from AgenteA import AgenteA
from AgenteB import AgenteB

async def main():
    agente_a = AgenteA("agentea@localhost", "password")
    agente_b = AgenteB("agenteb@localhost", "password")

    await agente_b.start()
    await agente_a.start()

    await asyncio.sleep(10)

    await agente_a.stop()
    await agente_b.stop()

asyncio.run(main())