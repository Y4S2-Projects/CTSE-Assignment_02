import os
import sys
import unittest
from unittest.mock import patch

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.coordinator import coordinator_agent
from agents.evaluator import evaluator_agent
from agents.researcher import researcher_agent
from agents.writer import writer_agent
from core.state import state


class FakeChain:
    def __init__(self, response):
        self.response = response
        self.last_payload = None

    def invoke(self, payload):
        self.last_payload = payload
        return self.response


class FakeLLM:
    def __init__(self, response):
        self.response = response

    def __ror__(self, prompt):
        return FakeChain(self.response)


class FakePrompt:
    def __init__(self, response):
        self.response = response

    def __or__(self, llm):
        return FakeChain(self.response)


class TestAgentBehavior(unittest.TestCase):
    def setUp(self):
        state.state = {
            "question": None,
            "plan": None,
            "research": None,
            "draft": None,
            "evaluation": None,
        }

    @patch("agents.coordinator.log")
    @patch("agents.coordinator.PromptTemplate.from_template")
    @patch("agents.coordinator.OllamaLLM")
    def test_coordinator_agent_generates_plan_and_updates_state(
        self,
        mock_llm,
        mock_prompt,
        _mock_log,
    ):
        expected_plan = (
            "Step 1: Research DevOps.\n"
            "Step 2: Draft the answer.\n"
            "Step 3: Review and improve."
        )
        mock_llm.return_value = FakeLLM(expected_plan)
        mock_prompt.return_value = FakePrompt(expected_plan)

        plan = coordinator_agent("Explain DevOps")

        self.assertEqual(plan, expected_plan)
        self.assertEqual(state.get("question"), "Explain DevOps")
        self.assertEqual(state.get("plan"), expected_plan)

    @patch("agents.researcher.log")
    @patch("agents.researcher.PromptTemplate.from_template")
    @patch("agents.researcher.OllamaLLM")
    def test_researcher_agent_generates_research_from_question(
        self,
        mock_llm,
        mock_prompt,
        _mock_log,
    ):
        state.update("question", "Explain neural networks")
        expected_research = "Neural networks are computing systems inspired by connected neurons."
        mock_llm.return_value = FakeLLM(expected_research)
        mock_prompt.return_value = FakePrompt(expected_research)

        research = researcher_agent()

        self.assertEqual(research, expected_research)
        self.assertEqual(state.get("research"), expected_research)

    @patch("agents.researcher.log")
    def test_researcher_agent_handles_missing_question(self, _mock_log):
        research = researcher_agent()

        self.assertEqual(research, "No research conducted.")
        self.assertIsNone(state.get("research"))

    @patch("agents.writer.log")
    @patch("agents.writer.PromptTemplate.from_template")
    @patch("agents.writer.OllamaLLM")
    def test_writer_agent_generates_draft_and_updates_state(
        self,
        mock_llm,
        mock_prompt,
        _mock_log,
    ):
        state.update("question", "Explain cloud computing")
        state.update("research", "Cloud computing provides on-demand computing resources.")
        expected_draft = (
            "Introduction\nCloud computing is important.\n\n"
            "Explanation\nIt provides services over the internet.\n\n"
            "Conclusion\nCloud computing improves scalability."
        )
        mock_llm.return_value = FakeLLM(expected_draft)
        mock_prompt.return_value = FakePrompt(expected_draft)

        draft = writer_agent()

        self.assertEqual(draft, expected_draft)
        self.assertEqual(state.get("draft"), expected_draft)

    @patch("agents.evaluator.log")
    def test_evaluator_agent_requests_improvement_for_short_draft(self, _mock_log):
        state.update("draft", "Introduction\nShort draft.\nConclusion\nDone.")

        evaluation = evaluator_agent()

        self.assertEqual(evaluation["status"], "Improve")
        self.assertIn("Length is too short", evaluation["feedback"])
        self.assertEqual(state.get("evaluation"), evaluation)

    @patch("agents.evaluator.log")
    def test_evaluator_agent_accepts_complete_draft(self, _mock_log):
        long_body = " ".join(["well explained content"] * 110)
        state.update(
            "draft",
            f"Introduction\n{long_body}\n\nConclusion\nThis completes the assignment.",
        )

        evaluation = evaluator_agent()

        self.assertEqual(evaluation["status"], "Good")
        self.assertIn("meets all academic requirements", evaluation["feedback"])
        self.assertEqual(state.get("evaluation"), evaluation)


if __name__ == "__main__":
    unittest.main()
