from core.state import state
from core.logger import log
from tools.search_tool import search_knowledge

def researcher_agent() -> str:
    """Researcher Agent: Uses the search tool to find information based on the plan.
    
    Returns:
        str: The gathered research.
    """
    question = state.get("question")
    plan = state.get("plan")
    
    log("Researcher", "Starting research based on the plan.")
    
    if not question:
        log("Researcher", "No question found in state.")
        return "No research conducted."
        
    research_data = search_knowledge(question)
    
    log("Researcher", f"Research completed. Found data.")
    state.update("research", research_data)
    
    return research_data
