import unittest
from campus_taskflow.adk.core import State
from campus_taskflow.agents.orchestrator import OrchestratorAgent
from campus_taskflow.agents.scheduler import SchedulerAgent

class TestAgents(unittest.TestCase):
    def test_scheduler_agent(self):
        agent = SchedulerAgent()
        state = State()
        state.set("parsed_tasks", [{"description": "Test Task", "deadline": None}])
        
        schedule = agent.run(state, None)
        self.assertTrue(len(schedule) > 0)
        self.assertEqual(schedule[0]['task'], "Test Task")

    def test_orchestrator_init(self):
        agent = OrchestratorAgent()
        self.assertEqual(len(agent.agents), 6)

if __name__ == '__main__':
    unittest.main()
