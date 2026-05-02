from core.state import state
from core.logger import log
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def researcher_agent() -> str:
    """Researcher Agent: Uses LLM to generate detailed research."""
    question = state.get("question")
    
    log("Researcher", "Starting research generation with LLM.")
    
    if not question:
        log("Researcher", "No question found in state.")
        return "No research conducted."
        
    llm = OllamaLLM(model="llama3")
    prompt = PromptTemplate.from_template(
        "You are an expert Researcher. Explain in detail: {question}\n\n"
        "Ensure your response is between 150-300 words and covers:\n"
        "- Definition\n"
        "- Explanation\n"
        "- Real-world examples\n"
        "- Key concepts\n\n"
        "Research Output:"
    )
    
    try:
        chain = prompt | llm
        research_data = chain.invoke({"question": question})
    except Exception as e:
        log("Researcher", f"Error generating research with Ollama: {e}")
        research_data = f"Fallback research for {question}. Definitions, examples, and key concepts."
    
    log("Researcher", "Research completed successfully.")
    state.update("research", research_data)
    
    return research_data
