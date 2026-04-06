import asyncio
import time

import jsonpickle
from pydantic import BaseModel
from spade.agent import Agent, Message
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, Template
from model.data_model import EnvironmentData
from utilities import helper


ontology_list = ["sensor_activity"]

class EnvironmentAgent(Agent):

    class ReceiveBehaviourEnvironmentAgent(CyclicBehaviour):
        global ontology_list
        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                conv_id = msg.get_metadata("conversation-id")
                perf = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                
                print(f"[EnvironmentAgent] Mensagem recebida: : perf={perf}, ontology={ontology}, conv_id={conv_id}")
                
                if perf == "request":
                    print(f"[EnvironmentAgent] REQUEST recebida (conv_id={conv_id})")

                    data = jsonpickle.decode(msg.body)
                    print(ontology_list)
                    if ontology not in ontology_list:
                        print(f"[EnvironmentAgent] Ontology desconhecida: {ontology}")
                        # FAILURE
                        failure = msg.make_reply()
                        failure.set_metadata("performative", "failure")
                        failure.set_metadata("ontology", ontology)
                        failure.set_metadata("conversation-id", conv_id)
                        failure.body = f"Ontology '{ontology}' não suportada"
                        print(f"[EnvironmentAgent] FAILURE enviada (conv_id={conv_id})")
                        await self.send(failure)
                        return
                    
                    # AGREE
                    agree = msg.make_reply()
                    agree.set_metadata("performative", "agree")
                    agree.set_metadata("ontology", ontology)
                    agree.set_metadata("conversation-id", conv_id)
                    
                    print(f"[EnvironmentAgent] AGREE enviada (conv_id={conv_id})")
                    
                    await self.send(agree)
                    await asyncio.sleep(0.5)  # simular processamento
                    try:

                        # processamento
                        result = {
                            "status": "processed",
                            "user": data.utilizador_id,
                            "conv_id": conv_id,
                            "environment_data": EnvironmentData(
                                musica_id="1",
                                musica_nome="1",
                                musica_banda="1",
                                musica_tipo_id="1",
                                musica_tipo_nome="1",
                                quantidade_pessoas_sala=1,
                                quantidade_pessoas_sala_actividade=1,
                                quantidade_pessoas_sala_paradas=1,
                                atividade_media_sala=0.1,
                                interesse_medio_sala=0.2,
                                matching_list_sal=helper.generate_mock_matching_list(5)
                            ).dict()
                        }

                        # INFORM
                        inform = msg.make_reply()
                        inform.set_metadata("performative", "inform")
                        inform.set_metadata("ontology", ontology)
                        inform.set_metadata("conversation-id", conv_id)
                        inform.body = jsonpickle.encode(result)

                        if(ontology == "sensor_activity"):
                            print("[EnvironmentAgent] Processar sensor_activity ontology", ontology)

                        print(f"[EnvironmentAgent] INFORM enviada (conv_id={conv_id})")
                        await self.send(inform)

                    except Exception as e:
                        # FAILURE
                        failure = msg.make_reply()
                        failure.set_metadata("performative", "failure")
                        failure.set_metadata("ontology", ontology)
                        failure.set_metadata("conversation-id", conv_id)
                        failure.body = str(e)
                        print(f"[EnvironmentAgent] FAILURE enviada (conv_id={conv_id}, exception={e})")
                        await self.send(failure)

    async def setup(self):
        print("EnvironmentAgent iniciado")
        self.add_behaviour(self.ReceiveBehaviourEnvironmentAgent())