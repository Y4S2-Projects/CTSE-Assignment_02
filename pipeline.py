from core.state import state
from core.logger import log
from agents.coordinator import coordinator_agent
from agents.researcher import researcher_agent
from agents.writer import writer_agent
from agents.evaluator import evaluator_agent

def run_system(question: str) -> tuple[str, dict, dict]:
    """Runs the multi-agent system pipeline sequentially with an iterative refinement loop.
    
    Args:
        question (str): The question to answer.
        
    Returns:
        tuple: (final_answer, evaluation, full_state)
    """
    log("System", f"--- Starting pipeline for question: '{question}' ---")
    
    # Run initial pipeline phases
    coordinator_agent(question)
    researcher_agent()
    
    # Iterative Improvement Loop
    MAX_ITERATIONS = 2
    feedback = ""
    
    for i in range(MAX_ITERATIONS):
        log("System", f"--- Iteration {i+1} of Writer/Evaluator Loop ---")
        
        final_answer = writer_agent(feedback)
        evaluation = evaluator_agent()
        
        if evaluation.get("status") == "Good":
            log("System", "Draft evaluated as 'Good'. Exiting refinement loop.")
            break
        else:
            feedback = evaluation.get("feedback", "Improve the previous answer.")
            log("System", f"Draft evaluated as 'Improve'. Providing feedback to writer: {feedback}")
    
    log("System", "--- Pipeline execution finished ---")
    
    return final_answer, evaluation, state.show()

if __name__ == "__main__":
    # Get the question from the user interactively
    question = input("\n📝 Enter your question: ")
    
    answer, eval_result, full_state = run_system(question)
    print("\nFINAL ANSWER:\n")
    print(answer)
    print("\nEVALUATION:\n", eval_result)
