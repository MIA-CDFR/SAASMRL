import jsonpickle
import requests
 
from spade.behaviour import CyclicBehaviour
from agents.base_background_agent import BaseBackgroundAgent
from config.config import AgentAddresses, AgentOntologies, AgentPerformatives, SeververConfig
from model.user_matching_cluster import UserMatchingClusterModel


SERVER_URL = f"http://{SeververConfig.SERVER_HOSTNAME}:{SeververConfig.SERVER_PORT}"


class MatchingAgent(BaseBackgroundAgent):

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.cluster_model = UserMatchingClusterModel()

    def _notify_invites(self, payload):
        matching_result = payload.get("matching_result", {})
        requester = payload.get("user_id") or payload.get("device_id")

        for match in matching_result.get("matches", []):
            matched_user_id = match.get("user_id")
            if not matched_user_id:
                continue

            invite_data = {
                "type": "invite",
                "from_user_id": requester,
                "to_user_id": matched_user_id,
                "cluster_id": matching_result.get("cluster_id"),
                "compatibility_score": match.get("score"),
                "distance_km": match.get("distance_km"),
            }

            try:
                requests.post(
                    f"{SERVER_URL}/set_user_match/{matched_user_id}",
                    json=invite_data,
                    timeout=3,
                )
            except Exception as e:
                print(f"[MatchingAgent] Erro ao publicar convite para API: {e}")
         
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
                                payload = self.agent.cluster_model.process_matching_request(payload)
                                self.agent._notify_invites(payload)

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
