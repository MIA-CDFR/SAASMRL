import asyncio
import threading
import jsonpickle
 
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, Message
from agents.base_background_agent import BaseBackgroundAgent
from config.config import AGENT_PASSWORD, AgentAddresses, AgentOntologies, AgentPerformatives

class DatabaseAgent(BaseBackgroundAgent):
 
    class ReceiveDatabaseDataBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
 
            if msg:
                print("\n[DatabaseAgent] Mensagem recebida")
 
                sender = msg.sender
                performative = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                conversation_id = msg.get_metadata("conversation-id")
                
                print(f"[DatabaseAgent] Performative: {performative}")
                print(f"[DatabaseAgent] Ontology: {ontology}")
                print(f"[DatabaseAgent] Conversation ID: {conversation_id}")
 
                try:
                    payload = jsonpickle.decode(msg.body)
 
                    print("**********[DatabaseAgent] Payload recebido:")
                    print(payload)
 
                    if ontology == AgentOntologies.SENSOR_ACTIVITY:
                        if performative == AgentPerformatives.REQUEST:

                            print("**********[DatabaseAgent] A processar dados de atividade")
                            try:
                                  await self.agent.forward_message(
                                    behaviour=self,
                                    payload=payload,
                                    agent_to=sender,
                                    performative=AgentPerformatives.INFORM,
                                    ontology=AgentOntologies.SENSOR_ACTIVITY,
                                    conversation_id=conversation_id
                                )           
                            except Exception as e:
                                print(f"[DatabaseAgent] Erro ao enviar mensagem para DatabaseAgent: {e}")

                            print("**********[DatabaseAgent] Forward concluído")

                        elif performative == AgentPerformatives.INFORM:
                            print("[DatabaseAgent] INFORM recebido - dados de atividade processados") 
 
                except Exception as e:
                    print(f"[DatabaseAgent] Erro ao processar mensagem: {e}")
 
            else:
                print("[DatabaseAgent] Nenhuma mensagem recebida")
 
    async def setup(self):
        print(f"[DatabaseAgent] {self.jid} iniciado - setup")
        self.add_behaviour(self.ReceiveDatabaseDataBehaviour())
 