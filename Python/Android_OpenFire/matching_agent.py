from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json

from matching import encontrar_matches
from firebase_db import save_match


class MatchingAgent(Agent):

    class MatchBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                data = json.loads(msg.body)

                matches = encontrar_matches(data)

                for m in matches:
                    print("MATCH ENCONTRADO:")
                    print(m)
                    save_match(m)

    async def setup(self):
        print("MatchingAgent iniciado")
        self.add_behaviour(self.MatchBehaviour())