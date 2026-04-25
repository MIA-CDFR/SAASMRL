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
        invites = matching_result.get("invites", [])

        print(f"[MatchingAgent] Notificando convites para API: {invites}")

        for invite in invites:
            target_user_id = invite.get("to_user_id")
            from_user_id = invite.get("from_user_id")
            solo = invite.get("solo_mode", False)

            # Build the base invite payload
            base = {
                "type": invite.get("type", "invite"),
                "id": invite.get("invite_id"),
                "cluster": invite.get("cluster", matching_result.get("cluster", "Iniciante")),
                "from_user_id": from_user_id,
                "to_user_id": target_user_id,
                "distance_km": invite.get("distance_km"),
                "same_city": invite.get("same_city"),
                "city": invite.get("city"),
            }
            #@TODO Verificar quando e quem deve receber as mensagens
            # Notify the target user
            if target_user_id:
                try:
                    requests.post(
                        f"{SERVER_URL}/set_user_match/{target_user_id}",
                        json=base,
                        timeout=3,
                    )
                except Exception as e:
                    print(f"[MatchingAgent] Erro ao publicar convite para {target_user_id}: {e}")

            # Also notify the source (from) user with a mirrored invite,
            # unless it is a solo event (from == to already handled above)
            if from_user_id and from_user_id != target_user_id and not solo:
                mirrored = {**base, "to_user_id": from_user_id, "from_user_id": target_user_id}
                try:
                    requests.post(
                        f"{SERVER_URL}/set_user_match/{from_user_id}",
                        json=mirrored,
                        timeout=3,
                    )
                except Exception as e:
                    print(f"[MatchingAgent] Erro ao publicar convite espelhado para {from_user_id}: {e}")
         
    class ReceiveMatchingDataBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
 
            if msg:
                print("\n[MatchingAgent] Mensagem recebida")
 
                sender = msg.sender
                performative = msg.get_metadata("performative")
                ontology = msg.get_metadata("ontology")
                conversation_id = msg.get_metadata("conversation-id")
 
                print(f"[MatchingAgent] Performative: {performative}")
                print(f"[MatchingAgent] Ontology: {ontology}")
                print(f"[MatchingAgent] Conversation ID: {conversation_id}")
 
                try:
                    payload = jsonpickle.decode(msg.body)
 
                    print("**********[MatchingAgent] Payload recebido:")
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
