from agents.sensor_agent import SensorAgent
from agents.preprocessing_agent import PreprocessingAgent
from agents.har_agent import HARAgent
from agents.profiling_agent import ProfilingAgent
from agents.matching_agent import MatchingAgent
from agents.safety_agent import SafetyAgent
from agents.interface_agent import InterfaceAgent


class CoordinatorAgent:
    def __init__(self):
        self.interface = InterfaceAgent()
        self.matching = MatchingAgent(self.interface)
        self.safety = SafetyAgent(self.interface)
        self.profiling = ProfilingAgent(self.matching)
        self.har = HARAgent(self.profiling, self.safety)
        self.preprocessing = PreprocessingAgent(self.har)
        self.sensor = SensorAgent(self.preprocessing)