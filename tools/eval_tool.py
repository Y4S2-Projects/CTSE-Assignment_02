def evaluate_output(answer: str) -> dict:
    """Evaluates the provided answer based on criteria.
    
    Args:
        answer (str): The text to evaluate.
        
    Returns:
        dict: A dictionary containing 'score' and 'status'.
    """
    score = 0
    if "Introduction" in answer or "introduction" in answer.lower():
        score += 30
    if "Conclusion" in answer or "conclusion" in answer.lower():
        score += 30
    if len(answer) > 100:
        score += 40
        
    status = "Passed" if score >= 70 else "Failed"
    
    return {
        "score": score,
        "status": status
    }
