import asyncio
import time

import jsonpickle
from pydantic import BaseModel
from spade.agent import Agent, Message
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, Template
from model.data_model import CalculatedActivityData
from utilities import helper


ontology_list = ["sensor_activity"]

class HARAgent(Agent):

    class ReceiveBehaviourHARAgent(CyclicBehaviour):
        global ontology_list
        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                conv_id = msg.get_metadata("conversation-id")
                perf = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                
                print(f"[HARAgent] Mensagem recebida: : perf={perf}, ontology={ontology}, conv_id={conv_id}")
                
                if perf == "request":
                    print(f"[HARAgent] REQUEST recebida (conv_id={conv_id})")

                    data = jsonpickle.decode(msg.body)
                    print(ontology_list)
                    if ontology not in ontology_list:
                        print(f"[HARAgent] Ontology desconhecida: {ontology}")
                        # FAILURE
                        failure = msg.make_reply()
                        failure.set_metadata("performative", "failure")
                        failure.set_metadata("ontology", ontology)
                        failure.set_metadata("conversation-id", conv_id)
                        failure.body = f"Ontology '{ontology}' não suportada"
                        print(f"[HARAgent] FAILURE enviada (conv_id={conv_id})")
                        await self.send(failure)
                        return
                    
                    # AGREE
                    agree = msg.make_reply()
                    agree.set_metadata("performative", "agree")
                    agree.set_metadata("ontology", ontology)
                    agree.set_metadata("conversation-id", conv_id)
                    
                    print(f"[HARAgent] AGREE enviada (conv_id={conv_id})")
                    
                    await self.send(agree)
                    await asyncio.sleep(0.5)  # simular processamento
                    try:

                        # processamento
                        result = {
                            "status": "processed",
                            "user": data.utilizador_id,
                            "conv_id": conv_id,
                            "calculated_activity_data": CalculatedActivityData(
                                actividade="1",
                                interesse="2",
                                timestamp="3",
                                timestamp_dia_semana="4",
                                timestamp_dia_periodo="5",
                                timestamp_hora="6",
                                timestamp_dia="7",
                                timestamp_mes="8",
                                timestamp_ano="9",
                            ).dict()
                        }


                        # INFORM
                        inform = msg.make_reply()
                        inform.set_metadata("performative", "inform")
                        inform.set_metadata("ontology", ontology)
                        inform.set_metadata("conversation-id", conv_id)
                        inform.body = jsonpickle.encode(result)

                        if(ontology == "sensor_activity"):
                            print("[HARAgent] Processar sensor_activity ontology", ontology)

                        print(f"[HARAgent] INFORM enviada (conv_id={conv_id})")
                        await self.send(inform)

                    except Exception as e:
                        # FAILURE
                        failure = msg.make_reply()
                        failure.set_metadata("performative", "failure")
                        failure.set_metadata("ontology", ontology)
                        failure.set_metadata("conversation-id", conv_id)
                        failure.body = str(e)
                        print(f"[HARAgent] FAILURE enviada (conv_id={conv_id}, exception={e})")
                        await self.send(failure)

    async def setup(self):
        print("HARAgent iniciado")
        self.add_behaviour(self.ReceiveBehaviourHARAgent())