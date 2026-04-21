from spade.agent import Agent
from spade.message import Message
from spade.template import Template
import jsonpickle


class BaseAgent(Agent):

    async def build_request(self, to, ontology, data, conversation_id):
        msg = Message(to=to)
        msg.set_metadata("performative", "request")
        msg.set_metadata("ontology", ontology)
        msg.set_metadata("conversation-id", conversation_id)
        msg.body = jsonpickle.encode(data)
        return msg
        #await self.container.send(msg)

    # async def request_and_wait(self, to, ontology, data, conversation_id):
    #     #await self.send_request(to, ontology, data, conversation_id)
    #     return await self.wait_for_reply(conversation_id)
    
    async def wait_for_reply(self, behaviour, conversation_id, timeout=10):

        template_agree = Template()
        template_agree.set_metadata("conversation-id", conversation_id)
        template_agree.set_metadata("performative", "agree")

        template_inform = Template()
        template_inform.set_metadata("conversation-id", conversation_id)
        template_inform.set_metadata("performative", "inform")

        template_failure = Template()
        template_failure.set_metadata("conversation-id", conversation_id)
        template_failure.set_metadata("performative", "failure")

        agree = await behaviour.receive(template=template_agree, timeout=timeout)
        if not agree:
            return None, "no_agree"

        inform = await behaviour.receive(template=template_inform, timeout=timeout)
        if inform:
            return jsonpickle.decode(inform.body), "inform"

        failure = await behaviour.receive(template=template_failure, timeout=timeout)
        if failure:
            return failure.body, "failure"

        return None, "timeout"