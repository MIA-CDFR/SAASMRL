import asyncio
import threading
import jsonpickle
 
from spade.agent import Agent, Message
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from agents.base_background_agent import BaseBackgroundAgent
from agents.base_sender_agent import BaseSenderAgent
from config.config import AGENT_PASSWORD, AgentAddresses, AgentOntologies, AgentPerformatives


class MatchingAgent(BaseBackgroundAgent):
         
    class ReceiveMatchingDataBehaviour(CyclicBehaviour):
    # class ReceiveMatchingDataBehaviour(PeriodicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
 
            if msg:
                print("\n[MatchingAgent] Mensagem recebida")
 
                sender = msg.sender
                performative = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                conversation_id = msg.get_metadata("conversation-id")
 
                print(f"[SensorAgent] Performative: {performative}")
                print(f"[SensorAgent] Ontology: {ontology}")
                print(f"[SensorAgent] Conversation ID: {conversation_id}")
 
                try:
                    payload = jsonpickle.decode(msg.body)
 
                    print("**********[SensorAgent] Payload recebido:")
                    print(payload)
 
                    if ontology == AgentOntologies.MATCHING:
                        if performative == AgentPerformatives.REQUEST:
                            
                            print(f"**********[MatchingAgent] A processar dados {AgentOntologies.MATCHING}")
                            try:
                                await self.agent.forward_message(
                                    behaviour=self,
                                    payload=payload,
                                    agent_to=AgentAddresses.COORDINATOR_AGENT,
                                    performative=AgentPerformatives.REQUEST,
                                    ontology=AgentOntologies.MATCHING,
                                    conversation_id=conversation_id
                                )

                                print("[MatchingAgent] Forward concluído")
                            except Exception as e:
                                print(f"[MatchingAgent] Erro ao enviar mensagem para CoordinatorAgent: {e}")

                            print("**********[MatchingAgent] Forward concluído")

                        elif performative == AgentPerformatives.INFORM:
                            print("[MatchingAgent] INFORM recebido - dados de atividade processados")
 
                except Exception as e:
                    print(f"[MatchingAgent] Erro ao processar mensagem: {e}")
 
            else:
                print("[MatchingAgent] Nenhuma mensagem recebida")
 
    async def setup(self):
        print(f"[MatchingAgent] {self.jid} iniciado - setup")
        await super().setup()
        self.add_behaviour(self.ReceiveMatchingDataBehaviour())
