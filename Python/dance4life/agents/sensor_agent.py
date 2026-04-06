import asyncio
import uuid
import time
import jsonpickle
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, Template
from spade.message import Message
from agents import api_agent
#from agents.base_agent import BaseAgent

# class SensorAgent(BaseAgent):

#     class RequestBehaviourSendToCoordinator(OneShotBehaviour):

#         async def run(self):
#             try:
#                 # await self.agent.send_request(
#                 #     to=self.receiver,
#                 #     ontology=self.ontology,
#                 #     data=self.data,
#                 #     conversation_id=self.conversation_id
#                 # )

#                 result, status = await self.agent.request_and_wait(
#                     to=self.receiver,
#                     ontology=self.ontology,
#                     data=self.data,
#                     conversation_id=self.conversation_id
#                 )

#                 if status == "inform":
#                     print("[ApiAgent] INFORM:", result)
#                     self.future.set_result(True)

#                 elif status == "failure":
#                     print("[ApiAgent] FAILURE:", result)
#                     self.future.set_result(False)

#                 else:
#                     print("[ApiAgent] Timeout ou erro")
#                     self.future.set_result(False)

#             except Exception as e:
#                 print("[ApiAgent] Erro:", e)
#                 self.future.set_result(False)


ontology_list = ["sensor_activity"]


class SensorAgent(Agent):

    class ReceiveBehaviourSensorAgent(CyclicBehaviour):
        global ontology_list
        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                conv_id = msg.get_metadata("conversation-id")
                perf = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                
                print(f"[SensorAgent] Mensagem recebida: : perf={perf}, ontology={ontology}, conv_id={conv_id}")
                
                if perf == "request":
                    print(f"[SensorAgent] REQUEST recebida (conv_id={conv_id})")

                    data = jsonpickle.decode(msg.body)
                    print(ontology_list)
                    if ontology not in ontology_list:
                        print(f"[SensorAgent] Ontology desconhecida: {ontology}")
                        # FAILURE
                        failure = msg.make_reply()
                        failure.set_metadata("performative", "failure")
                        failure.set_metadata("ontology", ontology)
                        failure.set_metadata("conversation-id", conv_id)
                        failure.body = f"Ontology '{ontology}' não suportada"
                        print(f"[SensorAgent] FAILURE enviada (conv_id={conv_id})")
                        await self.send(failure)
                        return
                    
                    # AGREE
                    agree = msg.make_reply()
                    agree.set_metadata("performative", "agree")
                    agree.set_metadata("ontology", ontology)
                    agree.set_metadata("conversation-id", conv_id)
                    
                    print(f"[SensorAgent] AGREE enviada (conv_id={conv_id})")
                    
                    await self.send(agree)
                    await asyncio.sleep(0.5)  # simular processamento

                    result_ok = False

                    if ontology == "sensor_activity":
                        print("[SensorAgent] Processar sensor_activity ontology", ontology)

                        future_sa = asyncio.get_running_loop().create_future()

                        behaviour_sa = self.agent.RequestBehaviourSendToCoordinator(
                            ontology="sensor_activity",
                            data=data,
                            receiver="coordinator_agent@localhost",
                            conversation_id=conv_id,
                            future=future_sa
                        )

                        self.agent.add_behaviour(behaviour_sa)

                        # ESPERAR PELO RESULTADO
                        result_ok = await future_sa

                    try:
                        result = {
                            "status": "processed" if result_ok else "failed",
                            "user": data.utilizador_id,
                            "conv_id": conv_id
                        }

                        # INFORM
                        inform = msg.make_reply()
                        inform.set_metadata("performative", "inform")
                        inform.set_metadata("ontology", ontology)
                        inform.set_metadata("conversation-id", conv_id)
                        inform.body = jsonpickle.encode(result)

                        if(ontology == "sensor_activity"):
                            print("[SensorAgent] Processar sensor_activity ontology", ontology)

                        print(f"[SensorAgent] INFORM enviada (conv_id={conv_id})")
                        await self.send(inform)

                    except Exception as e:
                        # FAILURE
                        failure = msg.make_reply()
                        failure.set_metadata("performative", "failure")
                        failure.set_metadata("ontology", ontology)
                        failure.set_metadata("conversation-id", conv_id)
                        failure.body = str(e)
                        print(f"[SensorAgent] FAILURE enviada (conv_id={conv_id}, exception={e})")
                        await self.send(failure)



    class RequestBehaviourSendToCoordinator(OneShotBehaviour):
        def __init__(self, ontology, data, receiver, conversation_id, future):
            super().__init__()
            self.data = data
            self.ontology = ontology
            self.receiver = receiver
            self.conversation_id = conversation_id
            self.future = future
            
        async def run(self):
            try:
                print(f"[SensorAgent] Envia Request para {self.receiver} (conv_id={self.conversation_id})")

                # Criar mensagem REQUEST
                msg = Message(to=self.receiver)
                msg.set_metadata("performative", "request")
                msg.set_metadata("ontology", self.ontology)
                msg.set_metadata("conversation-id", self.conversation_id)

                msg.body = jsonpickle.encode(self.data)

                await self.send(msg)

                # Template para garantir que só recebemos respostas desta conversa
                template = Template()
                template.set_metadata("conversation-id", self.conversation_id)

                agree_received = False
                start_time = time.time()
                timeout_total = 15  # segundos

                while True:
                    remaining_time = timeout_total - (time.time() - start_time)

                    if remaining_time <= 0:
                        print("[SensorAgent] Timeout total atingido")
                        self.future.set_result(False)
                        break

                    reply = await self.receive(timeout=remaining_time)

                    if reply and reply.get_metadata("conversation-id") != self.conversation_id:
                        continue  # ignora mensagens de outras conversas

                    if not reply:
                        print("[SensorAgent] Nenhuma resposta recebida")
                        self.future.set_result(False)
                        break

                    perf = reply.get_metadata("performative")
                    sender = str(reply.sender)

                    print(f"[SensorAgent] Mensagem recebida de {sender}: {perf}")

                    # Receção do AGREE
                    if perf == "agree":
                        print("[SensorAgent] AGREE recebido")
                        agree_received = True

                    # Receção do INFORM (resultado final)
                    elif perf == "inform":
                        result = jsonpickle.decode(reply.body)
                        print("[SensorAgent] INFORM recebido:", result)
                        self.future.set_result(True)
                        break

                    # FAILURE
                    elif perf == "failure":
                        print("[SensorAgent] FAILURE recebido:", reply.body)
                        self.future.set_result(False)
                        break

                    else:
                        print("[SensorAgent] Performative desconhecida:", perf)
                        self.future.set_result(False)

            except Exception as e:
                print("[SensorAgent] Erro:", e)
                self.future.set_result(False)

    async def setup(self):
        print("SensorAgent iniciado")
        self.add_behaviour(self.ReceiveBehaviourSensorAgent())