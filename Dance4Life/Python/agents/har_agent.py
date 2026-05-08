import asyncio
import threading
import jsonpickle
 
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, Message
from agents.base_background_agent import BaseBackgroundAgent
from config.config import AGENT_PASSWORD, AgentAddresses, AgentOntologies, AgentPerformatives

class HarAgent(BaseBackgroundAgent):
 
    class ReceiveHarDataBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
 
            if msg:
                #print("\n[HarAgent] Mensagem recebida")
 
                sender = msg.sender
                performative = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                conversation_id = msg.get_metadata("conversation-id")
                
                #print(f"[HarAgent] Performative: {performative}")
                #print(f"[HarAgent] Ontology: {ontology}")
                #print(f"[HarAgent] Conversation ID: {conversation_id}")
 
                try:
                    payload = jsonpickle.decode(msg.body)
 
                    #print("**********[HarAgent] Payload recebido:")
                    #print(payload)
 
                    if ontology == AgentOntologies.SENSOR_ACTIVITY:
                        if performative == AgentPerformatives.REQUEST:

                            #print("**********[HarAgent] A processar dados de atividade")
                            try:
                                await self.agent.forward_message(
                                    behaviour=self,
                                    payload=payload,
                                    agent_to=AgentAddresses.ENVIRONMENT_AGENT,
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
                                print(f"[HarAgent] Erro ao enviar mensagem para HarAgent: {e}")

                            #print("**********[HarAgent] Forward concluído")

                        elif performative == AgentPerformatives.INFORM:
                            print("[HarAgent] INFORM recebido - dados de atividade processados") 
 
                except Exception as e:
                    print(f"[HarAgent] Erro ao processar mensagem: {e}")
 
            else:
                print("[HarAgent] Nenhuma mensagem recebida")
 
    async def setup(self):
        #print(f"[HARAgent] {self.jid} iniciado - setup")
        await super().setup()
        self.add_behaviour(self.ReceiveHarDataBehaviour())
 