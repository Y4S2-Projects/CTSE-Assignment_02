import sys
import os
import unittest

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

    def test_run_system(self):
        question = "Explain neural networks"
        answer, evaluation, full_state = run_system(question)
        
        # 1. Assert: Answer contains "Introduction" (or at least draft generated)
        # Note: If ollama is not running, fallback text contains 'Introduction'
        self.assertIn("Introduction", answer)
        self.assertIn("Conclusion", answer)
        
        # 2. Assert: Evaluation status exists
        self.assertIn("status", evaluation)
        self.assertIn("score", evaluation)
        self.assertTrue(evaluation["score"] > 0)
        
        # 3. Assert full state is populated
        self.assertEqual(full_state["question"], question)
        self.assertIsNotNone(full_state["plan"])
        self.assertIsNotNone(full_state["research"])

if __name__ == '__main__':
    unittest.main()
