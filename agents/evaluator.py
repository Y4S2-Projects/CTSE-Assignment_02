from core.state import state
from core.logger import log
from tools.eval_tool import evaluate_output

def evaluator_agent() -> dict:
    """Evaluator Agent: Evaluates the draft quality.
    
    Returns:
        dict: The evaluation results.
    """
    draft = state.get("draft")
    
    log("Evaluator", "Starting evaluation of the draft.")
    
    if not draft:
        log("Evaluator", "No draft found to evaluate.")
        result = {"score": 0, "status": "Failed"}
    else:
        result = evaluate_output(draft)
        
    log("Evaluator", f"Evaluation completed: Score={result['score']}, Status={result['status']}")
    state.update("evaluation", result)
    
    return result
