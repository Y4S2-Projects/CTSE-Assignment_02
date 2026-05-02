from core.state import state
from core.logger import log

def evaluator_agent() -> dict:
    """Evaluator Agent: Evaluates the draft quality."""
    draft = state.get("draft")
    
    log("Evaluator", "Starting evaluation of the draft.")
    
    if not draft:
        log("Evaluator", "No draft found to evaluate.")
        result = {"status": "Improve", "feedback": "No draft generated."}
        state.update("evaluation", result)
        return result
        
    word_count = len(draft.split())
    missing_sections = []
    
    if "Introduction" not in draft and "introduction" not in draft.lower():
        missing_sections.append("Introduction")
    if "Conclusion" not in draft and "conclusion" not in draft.lower():
        missing_sections.append("Conclusion")
        
    feedback_notes = []
    
    if word_count < 300:
        feedback_notes.append(f"Length is too short ({word_count} words). Please expand to at least 300 words.")
    
    if missing_sections:
        feedback_notes.append(f"Missing required sections: {', '.join(missing_sections)}. Please add them.")
        
    if feedback_notes:
        feedback = " ".join(feedback_notes) + " Ensure better clarity and depth."
        status = "Improve"
    else:
        feedback = "The draft meets all academic requirements: good length, clear structure, and includes all necessary sections."
        status = "Good"
        
    result = {
        "status": status,
        "feedback": feedback
    }
    
    log("Evaluator", f"Evaluation completed: Status={result['status']}")
    log("Evaluator", f"Feedback: {result['feedback']}")
    
    state.update("evaluation", result)
    return result
