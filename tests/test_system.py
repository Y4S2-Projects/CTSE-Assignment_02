import sys
import os
import unittest
from unittest.mock import patch

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline import run_system
from core.state import state

class TestMultiAgentSystem(unittest.TestCase):
    def setUp(self):
        # Reset state before each test
        state.state = {
            "question": None,
            "plan": None,
            "research": None,
            "draft": None,
            "evaluation": None
        }

    @patch("pipeline.log")
    @patch("pipeline.evaluator_agent")
    @patch("pipeline.writer_agent")
    @patch("pipeline.researcher_agent")
    @patch("pipeline.coordinator_agent")
    def test_run_system(
        self,
        mock_coordinator,
        mock_researcher,
        mock_writer,
        mock_evaluator,
        _mock_log,
    ):
        question = "Explain neural networks"

        def fake_coordinator_agent(user_question):
            state.update("question", user_question)
            state.update("plan", "1. Research 2. Write 3. Evaluate")
            return state.get("plan")

        def fake_researcher_agent():
            state.update("research", "Research notes about neural networks.")
            return state.get("research")

        def fake_writer_agent(feedback=""):
            draft = (
                "Introduction\nNeural networks are machine learning models.\n\n"
                "Explanation\nThey learn patterns from data.\n\n"
                "Conclusion\nThey are useful for prediction and classification."
            )
            state.update("draft", draft)
            return draft

        def fake_evaluator_agent():
            evaluation = {
                "status": "Good",
                "feedback": "The draft includes the required structure.",
            }
            state.update("evaluation", evaluation)
            return evaluation

        mock_coordinator.side_effect = fake_coordinator_agent
        mock_researcher.side_effect = fake_researcher_agent
        mock_writer.side_effect = fake_writer_agent
        mock_evaluator.side_effect = fake_evaluator_agent

        answer, evaluation, full_state = run_system(question)
        
        # 1. Assert: Answer contains "Introduction" (or at least draft generated)
        self.assertIn("Introduction", answer)
        self.assertIn("Conclusion", answer)
        
        # 2. Assert: Evaluation status exists
        self.assertIn("status", evaluation)
        self.assertIn("feedback", evaluation)
        self.assertEqual(evaluation["status"], "Good")
        
        # 3. Assert full state is populated
        self.assertEqual(full_state["question"], question)
        self.assertIsNotNone(full_state["plan"])
        self.assertIsNotNone(full_state["research"])
        self.assertIsNotNone(full_state["draft"])
        self.assertIsNotNone(full_state["evaluation"])

if __name__ == '__main__':
    unittest.main()
