import asyncio
import threading
import jsonpickle
 
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, Message
from agents.base_background_agent import BaseBackgroundAgent
from config.config import AGENT_PASSWORD, AgentAddresses, AgentOntologies, AgentPerformatives

class CoordinatorAgent(BaseBackgroundAgent):
 
    class ReceiveCoordinatorDataBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
 
            if msg:
                print("\n[CoordinatorAgent] Mensagem recebida")

                sender = msg.sender
                performative = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                conversation_id = msg.get_metadata("conversation-id")
 
                print(f"[CoordinatorAgent] Performative: {performative}")
                print(f"[CoordinatorAgent] Ontology: {ontology}")
                print(f"[CoordinatorAgent] Conversation ID: {conversation_id}")
 
                try:
                    payload = jsonpickle.decode(msg.body)
 
                    print("**********[CoordinatorAgent] Payload recebido:")
                    print(payload)
 
                    if ontology == AgentOntologies.SENSOR_ACTIVITY:
                        if performative == AgentPerformatives.REQUEST:

                            print("**********[CoordinatorAgent] A processar dados de atividade")
                            try:
                                
                                print("**********[CoordinatorAgent] Forward para EnvironmentAgent")
                                await self.agent.forward_message(
                                    behaviour=self,
                                    payload=payload,
                                    agent_to=AgentAddresses.HAR_AGENT,
                                    performative=AgentPerformatives.REQUEST,
                                    ontology=AgentOntologies.SENSOR_ACTIVITY,
                                    conversation_id=conversation_id
                                )

                                await self.agent.forward_message(
                                    behaviour=self,
                                    payload=payload,
                                    agent_to=sender,
                                    performative=AgentPerformatives.INFORM,
                                    ontology=AgentOntologies.SENSOR_ACTIVITY,
                                    conversation_id=conversation_id
                                )                             

                            except Exception as e:
                                print(f"[CoordinatorAgent] Erro ao enviar mensagem para CoordinatorAgent: {e}")

                            print("**********[CoordinatorAgent] Forward concluído")

                        elif performative == AgentPerformatives.INFORM:
                            print("[CoordinatorAgent] INFORM recebido - dados de atividade processados")

                    if ontology == AgentOntologies.MOVEMENT_RECOMMENDATION:
                        if performative == AgentPerformatives.REQUEST:

                            # 👉 aqui integras o modelo RL -@TODO: COMO ASSIM?????
                            # exemplo simples:
                            payload["recommendation"] = True  # ou resultado do modelo

                            await self.agent.forward_message(
                                behaviour=self,
                                payload=payload,
                                agent_to=AgentAddresses.DATABASE_AGENT,
                                performative=AgentPerformatives.REQUEST,
                                ontology=AgentOntologies.MOVEMENT_RECOMMENDATION,
                                conversation_id=conversation_id
                            )
 
                except Exception as e:
                    print(f"[CoordinatorAgent] Erro ao processar mensagem: {e}")
 
            else:
                print("[CoordinatorAgent] Nenhuma mensagem recebida")
 
    async def setup(self):
        print(f"[CoordinatorAgent] {self.jid} iniciado - setup")
        self.add_behaviour(self.ReceiveCoordinatorDataBehaviour())
 