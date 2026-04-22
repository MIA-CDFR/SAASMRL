import asyncio
import threading
import jsonpickle
 
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, Message
from agents.base_background_agent import BaseBackgroundAgent
from config.config import AGENT_PASSWORD, AgentAddresses, AgentOntologies, AgentPerformatives
from sensor.external_sensors import get_weather


class EnvironmentAgent(BaseBackgroundAgent):
 
    class EnvironmentDataBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
 
            if msg:
                print("\n[EnvironmentAgent] Mensagem recebida")
 
                sender = msg.sender
                performative = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                conversation_id = msg.get_metadata("conversation-id")
                
                print(f"[EnvironmentAgent] Performative: {performative}")
                print(f"[EnvironmentAgent] Ontology: {ontology}")
                print(f"[EnvironmentAgent] Conversation ID: {conversation_id}")
 
                try:
                    payload = jsonpickle.decode(msg.body)

                    # Enriquecer o payload com dados ambientais
                    payload.update({
                        "weather": get_weather(payload.get("latitude"), payload.get("longitude"))
                    })
 
                    print("**********[EnvironmentAgent] Payload recebido:")
                    print(payload)
 
                    if ontology == AgentOntologies.SENSOR_ACTIVITY:
                        if performative == AgentPerformatives.REQUEST:

                            print("**********[EnvironmentAgent] A processar dados de atividade")
                            try:
                                await self.agent.forward_message(
                                    behaviour=self,
                                    payload=payload,
                                    agent_to=AgentAddresses.DATABASE_AGENT,
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
                                print(f"[EnvironmentAgent] Erro ao enviar mensagem para EnvironmentAgent: {e}")

                            print("**********[EnvironmentAgent] Forward concluído")

                        elif performative == AgentPerformatives.INFORM:
                            print("[EnvironmentAgent] INFORM recebido - dados de atividade processados") 
 
                except Exception as e:
                    print(f"[EnvironmentAgent] Erro ao processar mensagem: {e}")
 
            else:
                print("[EnvironmentAgent] Nenhuma mensagem recebida")
 
    async def setup(self):
        print(f"[EnvironmentAgent] {self.jid} iniciado - setup")
        await super().setup()
        self.add_behaviour(self.EnvironmentDataBehaviour())
 