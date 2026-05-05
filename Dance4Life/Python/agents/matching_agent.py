import jsonpickle
import requests
 
from spade.behaviour import CyclicBehaviour
from agents.base_background_agent import BaseBackgroundAgent
from config.config import AgentAddresses, AgentOntologies, AgentPerformatives, SeververConfig
from model.user_matching_cluster import UserActivityClusterModel


SERVER_URL = f"http://{SeververConfig.SERVER_HOSTNAME}:{SeververConfig.SERVER_PORT}"


class ClusteringAgent(BaseBackgroundAgent):

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.cluster_model = UserActivityClusterModel()

    def _notify_cluster_invite(self, payload):
        matching_result = payload.get("matching_result", {})
        invites = matching_result.get("invites", [])
        cluster_progression = matching_result.get("cluster_progression", {})

        print(f"[ClusteringAgent] Notificando cluster para API: {invites}")

        for invite in invites:
            target_user_id = invite.get("to_user_id")

            base = {
                "type": invite.get("type", "invite"),
                "mode": invite.get("mode", "cluster_progression"),
                "id": invite.get("invite_id"),
                "cluster": invite.get("next_cluster", cluster_progression.get("next_cluster")),
                "from_user_id": invite.get("from_user_id"),
                "to_user_id": target_user_id,
                "city": invite.get("city"),
                "ritmo": invite.get("ritmo"),
                "progress_percentage": invite.get(
                    "progress_percentage", cluster_progression.get("progress_percentage", 0.0)
                ),
                "current_level_index": invite.get(
                    "current_level_index", cluster_progression.get("current_level_index", 0)
                ),
                "message": invite.get("message"),
            }

            if target_user_id:
                try:
                    requests.post(
                        f"{SERVER_URL}/set_user_match/{target_user_id}",
                        json=base,
                        timeout=3,
                    )
                except Exception as e:
                    print(f"[ClusteringAgent] Erro ao publicar cluster para {target_user_id}: {e}")

    def _notify_invites(self, payload):
        self._notify_cluster_invite(payload)
         
    class ReceiveClusteringDataBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
 
            if msg:
                print("\n[ClusteringAgent] Mensagem recebida")
 
                sender = msg.sender
                performative = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                conversation_id = msg.get_metadata("conversation-id")
 
                print(f"[ClusteringAgent] Performative: {performative}")
                print(f"[ClusteringAgent] Ontology: {ontology}")
                print(f"[ClusteringAgent] Conversation ID: {conversation_id}")
 
                try:
                    payload = jsonpickle.decode(msg.body)
 
                    print("**********[ClusteringAgent] Payload recebido:")
                    print(payload)
 
                    if ontology == AgentOntologies.MATCHING:
                        if performative == AgentPerformatives.REQUEST:
                            
                            print(f"**********[ClusteringAgent] A processar dados {AgentOntologies.MATCHING}")
                            try:
                                payload = self.agent.cluster_model.process_matching_request(payload)
                                self.agent._notify_cluster_invite(payload)

                                await self.agent.forward_message(
                                    behaviour=self,
                                    payload=payload,
                                    agent_to=AgentAddresses.COORDINATOR_AGENT,
                                    performative=AgentPerformatives.REQUEST,
                                    ontology=AgentOntologies.MATCHING,
                                    conversation_id=conversation_id
                                )

                                print("[ClusteringAgent] Forward concluído")
                            except Exception as e:
                                print(f"[ClusteringAgent] Erro ao enviar mensagem para CoordinatorAgent: {e}")

                            print("**********[ClusteringAgent] Forward concluído")

                        elif performative == AgentPerformatives.INFORM:
                            print("[ClusteringAgent] INFORM recebido - dados de atividade processados")
 
                except Exception as e:
                    print(f"[ClusteringAgent] Erro ao processar mensagem: {e}")
 
            else:
                print("[ClusteringAgent] Nenhuma mensagem recebida")
 
    async def setup(self):
        print(f"[ClusteringAgent] {self.jid} iniciado - setup")
        await super().setup()
        self.add_behaviour(self.ReceiveClusteringDataBehaviour())


MatchingAgent = ClusteringAgent
