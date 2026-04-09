import asyncio
import time

import jsonpickle
from spade.agent import Agent, Message
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, Template

ontology_list = ["sensor_activity"]

class CoordinatorAgent(Agent):

    class ReceiveBehaviourCoordinatorAgent(CyclicBehaviour):
        global ontology_list
        async def run(self):
            msg = await self.receive(timeout=10)

            if msg:
                conv_id = msg.get_metadata("conversation-id")
                perf = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                
                print(f"[CoordinatorAgent] Mensagem recebida: : perf={perf}, ontology={ontology}, conv_id={conv_id}")
                
                if perf == "request":
                    print(f"[CoordinatorAgent] REQUEST recebida (conv_id={conv_id})")

                    data = jsonpickle.decode(msg.body)
                    print(ontology_list)
                    if ontology not in ontology_list:
                        print(f"[CoordinatorAgent] Ontology desconhecida: {ontology}")
                        # FAILURE
                        failure = msg.make_reply()
                        failure.set_metadata("performative", "failure")
                        failure.set_metadata("ontology", ontology)
                        failure.set_metadata("conversation-id", conv_id)
                        failure.body = f"Ontology '{ontology}' não suportada"
                        print(f"[CoordinatorAgent] FAILURE enviada (conv_id={conv_id})")
                        await self.send(failure)
                        return
                    
                    # AGREE
                    agree = msg.make_reply()
                    agree.set_metadata("performative", "agree")
                    agree.set_metadata("ontology", ontology)
                    agree.set_metadata("conversation-id", conv_id)
                    
                    print(f"[CoordinatorAgent] AGREE enviada (conv_id={conv_id})")
                    
                    await self.send(agree)
                    await asyncio.sleep(0.5)  # simular processamento

                    result_ok_har = False
                    result_ok_env = False
                    result_ok_db = False

                    if ontology == "sensor_activity":
                        print("[CoordinatorAgent] Processar sensor_activity ontology", ontology)

                        future_har = asyncio.get_running_loop().create_future()

                        behaviour_har = self.agent.RequestBehaviourRequestFromHAR(
                            ontology="sensor_activity",
                            data=data,
                            receiver="har_agent@localhost",
                            conversation_id=conv_id,
                            future=future_har
                        )

                        self.agent.add_behaviour(behaviour_har)

                        # ESPERAR PELO RESULTADO
                        result_ok_har = await future_har


                        if result_ok_har:


                            print("[CoordinatorAgent] Processar sensor_activity ontology", ontology)

                            future_env = asyncio.get_running_loop().create_future()

                            behaviour_env = self.agent.RequestBehaviourRequestFromEnvironment(
                                ontology="sensor_activity",
                                data=data,
                                receiver="environment_agent@localhost",
                                conversation_id=conv_id,
                                future=future_env
                            )

                            self.agent.add_behaviour(behaviour_env)

                            # ESPERAR PELO RESULTADO
                            result_ok_env = await future_env           

                            if result_ok_env:
                                print("[CoordinatorAgent] Processar sensor_activity ontology", ontology)

                                future_db = asyncio.get_running_loop().create_future()

                                behaviour_db = self.agent.RequestBehaviourRequestToDatabase(
                                    ontology="sensor_activity",
                                    data=data,
                                    receiver="database_agent@localhost",
                                    conversation_id=conv_id,
                                    future=future_db
                                )

                                self.agent.add_behaviour(behaviour_db)

                                # ESPERAR PELO RESULTADO
                                result_ok_db = await future_db    

                                if result_ok_db:
                                    result = {
                                        "status": "processed",
                                        "user": data.utilizador_id,
                                        "conv_id": conv_id
                                    }
                        else:
                            result = {
                                "status": "error",
                                "user": data.utilizador_id,
                                "conv_id": conv_id
                            }


                    try:





                        # INFORM
                        inform = msg.make_reply()
                        inform.set_metadata("performative", "inform")
                        inform.set_metadata("ontology", ontology)
                        inform.set_metadata("conversation-id", conv_id)
                        inform.body = jsonpickle.encode(result)

                        if(ontology == "sensor_activity"):
                            print("[CoordinatorAgent] Processar sensor_activity ontology", ontology)

                        print(f"[CoordinatorAgent] INFORM enviada (conv_id={conv_id})")
                        await self.send(inform)

                    except Exception as e:
                        # FAILURE
                        failure = msg.make_reply()
                        failure.set_metadata("performative", "failure")
                        failure.set_metadata("ontology", ontology)
                        failure.set_metadata("conversation-id", conv_id)
                        failure.body = str(e)
                        print(f"[CoordinatorAgent] FAILURE enviada (conv_id={conv_id}, exception={e})")
                        await self.send(failure)


    class RequestBehaviourRequestFromHAR(OneShotBehaviour):
        def __init__(self, ontology, data, receiver, conversation_id, future):
            super().__init__()
            self.data = data
            self.ontology = ontology
            self.receiver = receiver
            self.conversation_id = conversation_id
            self.future = future
            
        async def run(self):
            try:
                print(f"[CoordinatorAgent] Envia Request para {self.receiver} (conv_id={self.conversation_id})")

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
                        print("[CoordinatorAgent] Timeout total atingido")
                        self.future.set_result(False)
                        break

                    reply = await self.receive(timeout=remaining_time)

                    if reply and reply.get_metadata("conversation-id") != self.conversation_id:
                        continue  # ignora mensagens de outras conversas

                    if not reply:
                        print("[CoordinatorAgent] Nenhuma resposta recebida")
                        self.future.set_result(False)
                        break

                    perf = reply.get_metadata("performative")
                    sender = str(reply.sender)

                    print(f"[CoordinatorAgent] Mensagem recebida de {sender}: {perf}")

                    # Receção do AGREE
                    if perf == "agree":
                        print("[CoordinatorAgent] AGREE recebido")
                        agree_received = True

                    # Receção do INFORM (resultado final)
                    elif perf == "inform":
                        result = jsonpickle.decode(reply.body)
                        print("[CoordinatorAgent] INFORM recebido:", result)
                        self.future.set_result(True)
                        break

                    # FAILURE
                    elif perf == "failure":
                        print("[CoordinatorAgent] FAILURE recebido:", reply.body)
                        self.future.set_result(False)
                        break

                    else:
                        print("[CoordinatorAgent] Performative desconhecida:", perf)
                        self.future.set_result(False)

            except Exception as e:
                print("[CoordinatorAgent] Erro:", e)
                self.future.set_result(False)

    class RequestBehaviourRequestFromEnvironment(OneShotBehaviour):
        def __init__(self, ontology, data, receiver, conversation_id, future):
            super().__init__()
            self.data = data
            self.ontology = ontology
            self.receiver = receiver
            self.conversation_id = conversation_id
            self.future = future
            
        async def run(self):
            try:
                print(f"[CoordinatorAgent] Envia Request para {self.receiver} (conv_id={self.conversation_id})")

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
                        print("[CoordinatorAgent] Timeout total atingido")
                        self.future.set_result(False)
                        break

                    reply = await self.receive(timeout=remaining_time)

                    if reply and reply.get_metadata("conversation-id") != self.conversation_id:
                        continue  # ignora mensagens de outras conversas

                    if not reply:
                        print("[CoordinatorAgent] Nenhuma resposta recebida")
                        self.future.set_result(False)
                        break

                    perf = reply.get_metadata("performative")
                    sender = str(reply.sender)

                    print(f"[CoordinatorAgent] Mensagem recebida de {sender}: {perf}")

                    # Receção do AGREE
                    if perf == "agree":
                        print("[CoordinatorAgent] AGREE recebido")
                        agree_received = True

                    # Receção do INFORM (resultado final)
                    elif perf == "inform":
                        result = jsonpickle.decode(reply.body)
                        print("[CoordinatorAgent] INFORM recebido:", result)
                        self.future.set_result(True)
                        break

                    # FAILURE
                    elif perf == "failure":
                        print("[CoordinatorAgent] FAILURE recebido:", reply.body)
                        self.future.set_result(False)
                        break

                    else:
                        print("[CoordinatorAgent] Performative desconhecida:", perf)
                        self.future.set_result(False)

            except Exception as e:
                print("[CoordinatorAgent] Erro:", e)
                self.future.set_result(False)                

    class RequestBehaviourRequestToDatabase(OneShotBehaviour):
        def __init__(self, ontology, data, receiver, conversation_id, future):
            super().__init__()
            self.data = data
            self.ontology = ontology
            self.receiver = receiver
            self.conversation_id = conversation_id
            self.future = future
            
        async def run(self):
            try:
                print(f"[CoordinatorAgent] Envia Request para {self.receiver} (conv_id={self.conversation_id})")

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
                        print("[CoordinatorAgent] Timeout total atingido")
                        self.future.set_result(False)
                        break

                    reply = await self.receive(timeout=remaining_time)

                    if reply and reply.get_metadata("conversation-id") != self.conversation_id:
                        continue  # ignora mensagens de outras conversas

                    if not reply:
                        print("[CoordinatorAgent] Nenhuma resposta recebida")
                        self.future.set_result(False)
                        break

                    perf = reply.get_metadata("performative")
                    sender = str(reply.sender)

                    print(f"[CoordinatorAgent] Mensagem recebida de {sender}: {perf}")

                    # Receção do AGREE
                    if perf == "agree":
                        print("[CoordinatorAgent] AGREE recebido")
                        agree_received = True

                    # Receção do INFORM (resultado final)
                    elif perf == "inform":
                        result = jsonpickle.decode(reply.body)
                        print("[CoordinatorAgent] INFORM recebido:", result)
                        self.future.set_result(True)
                        break

                    # FAILURE
                    elif perf == "failure":
                        print("[CoordinatorAgent] FAILURE recebido:", reply.body)
                        self.future.set_result(False)
                        break

                    else:
                        print("[CoordinatorAgent] Performative desconhecida:", perf)
                        self.future.set_result(False)

            except Exception as e:
                print("[CoordinatorAgent] Erro:", e)
                self.future.set_result(False)   

    async def setup(self):
        print("CoordinatorAgent iniciado")
        self.add_behaviour(self.ReceiveBehaviourCoordinatorAgent())