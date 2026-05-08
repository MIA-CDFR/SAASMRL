import asyncio
import threading
import jsonpickle
 
from spade.agent import Agent, Message
from spade.behaviour import CyclicBehaviour
from agents.base_background_agent import BaseBackgroundAgent
from agents.base_sender_agent import BaseSenderAgent
from config.config import AGENT_PASSWORD, AgentAddresses, AgentOntologies, AgentPerformatives
from spade.presence import PresenceType, PresenceShow

class SensorAgent(BaseBackgroundAgent):
         
    class ReceiveSensorDataBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
 
            if msg:
                #print("\n[SensorAgent] Mensagem recebida")
 
                sender = msg.sender
                performative = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                conversation_id = msg.get_metadata("conversation-id")
 
                #print(f"[SensorAgent] Performative: {performative}")
                #print(f"[SensorAgent] Ontology: {ontology}")
                #print(f"[SensorAgent] Conversation ID: {conversation_id}")
 
                try:
                    payload = jsonpickle.decode(msg.body)
 
                    #print("**********[SensorAgent] Payload recebido:")
                    #print(payload)
 
                    if ontology == AgentOntologies.SENSOR_ACTIVITY:
                        if performative == AgentPerformatives.REQUEST:

                            # LIXO   ***   print("**********[SensorAgent] A processar dados de atividade")
                            #print(f"**********[SensorAgent] A processar dados {AgentOntologies.SENSOR_ACTIVITY}")
                            try:
                                await self.agent.forward_message(
                                    behaviour=self,
                                    payload=payload,
                                    agent_to=AgentAddresses.COORDINATOR_AGENT,
                                    performative=AgentPerformatives.REQUEST,
                                    ontology=AgentOntologies.SENSOR_ACTIVITY,
                                    conversation_id=conversation_id
                                )

                                #print("[SensorAgent] Forward concluído")
                            except Exception as e:
                                print(f"[SensorAgent] Erro ao enviar mensagem para CoordinatorAgent: {e}")

                            #print("**********[SensorAgent] Forward concluído")

                        elif performative == AgentPerformatives.INFORM:
                            print("[SensorAgent] INFORM recebido - dados de atividade processados")
                    
                    if ontology == AgentOntologies.MOVEMENT_RECOMMENDATION:
                        if performative == AgentPerformatives.REQUEST:

                            #print(f"**********[SensorAgent] A processar dados {AgentOntologies.MOVEMENT_RECOMMENDATION}")

                            await self.agent.forward_message(
                                behaviour=self,
                                payload=payload,
                                agent_to=AgentAddresses.COORDINATOR_AGENT,
                                performative=AgentPerformatives.REQUEST,
                                ontology=AgentOntologies.MOVEMENT_RECOMMENDATION,
                                conversation_id=conversation_id
                            )
 
                except Exception as e:
                    print(f"[SensorAgent] Erro ao processar mensagem: {e}")
 
            else:
                print("[SensorAgent] Nenhuma mensagem recebida")
 
    async def setup(self):
        #print(f"[SensorAgent] {self.jid} iniciado - setup")
        await super().setup()
        self.add_behaviour(self.ReceiveSensorDataBehaviour())

