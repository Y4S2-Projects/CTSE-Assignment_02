from core.state import state
from core.logger import log
from agents.coordinator import coordinator_agent
from agents.researcher import researcher_agent
from agents.writer import writer_agent
from agents.evaluator import evaluator_agent

def run_system(question: str) -> tuple[str, dict, dict]:
    """Runs the multi-agent system pipeline sequentially.
    
    Args:
        question (str): The question to answer.
        
    Returns:
        tuple: (final_answer, evaluation, full_state)
    """
    log("System", f"--- Starting pipeline for question: '{question}' ---")
    
    # Run pipeline
    coordinator_agent(question)
    researcher_agent()
    final_answer = writer_agent()
    evaluation = evaluator_agent()
    
    log("System", "--- Pipeline execution finished ---")
    
    return final_answer, evaluation, state.show()

if __name__ == "__main__":
    # Get the question from the user interactively
    question = input("\n📝 Enter your question: ")
    
    answer, eval_result, full_state = run_system(question)
    print("\nFINAL ANSWER:\n")
    print(answer)
    print("\nEVALUATION:\n", eval_result)
