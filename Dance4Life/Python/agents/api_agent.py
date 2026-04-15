import jsonpickle
import uuid
import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template


#from agents.base_agent import BaseAgent

class ApiAgent(Agent):

    class RequestBehaviourSendSensorActivityToSensor(OneShotBehaviour):
        def __init__(self, ontology, data, receiver, future):
            super().__init__()
            self.data = data
            self.ontology = ontology
            self.receiver = receiver
            self.conversation_id = str(uuid.uuid4())
            self.future = future
            
        async def run(self):
            try:
                print(f"[ApiAgent] Envia Request para {self.receiver} (conv_id={self.conversation_id})")

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
                        print("[ApiAgent] Timeout total atingido")
                        self.future.set_result(False)
                        break

                    reply = await self.receive(timeout=remaining_time)

                    if not reply:
                        print("[ApiAgent] Nenhuma resposta recebida")
                        self.future.set_result(False)
                        break

                    perf = reply.get_metadata("performative")
                    sender = str(reply.sender)

                    print(f"[ApiAgent] Mensagem recebida de {sender}: {perf}")

                    # Receção do AGREE
                    if perf == "agree":
                        print("[ApiAgent] AGREE recebido")
                        agree_received = True

                    # Receção do INFORM (resultado final)
                    elif perf == "inform":
                        result = jsonpickle.decode(reply.body)
                        print("[ApiAgent] INFORM recebido:", result)
                        self.future.set_result(True)
                        break

                    # FAILURE
                    elif perf == "failure":
                        print("[ApiAgent] FAILURE recebido:", reply.body)
                        self.future.set_result(False)
                        break

                    else:
                        print("[ApiAgent] Performative desconhecida:", perf)
                        self.future.set_result(False)

            except Exception as e:
                print("[ApiAgent] Erro:", e)
                self.future.set_result(False)
