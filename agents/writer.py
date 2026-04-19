from core.state import state
from core.logger import log
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def writer_agent() -> str:
    """Writer Agent: Generates content based on the research.
    
    Returns:
        str: The generated draft.
    """
    question = state.get("question")
    research = state.get("research")
    
    log("Writer", "Starting draft generation based on research.")
    
    llm = OllamaLLM(model="llama3")
    prompt = PromptTemplate.from_template(
        "You are a Writer Agent. Write a structured response to the question based on the provided research. "
        "You MUST include 'Introduction', 'Explanation', and 'Conclusion' sections.\n\n"
        "Question: {question}\n"
        "Research: {research}\n\n"
        "Structured Output:"
    )
    
    try:
        chain = prompt | llm
        draft = chain.invoke({"question": question, "research": research})
    except Exception as e:
        log("Writer", f"Error generating draft with Ollama: {e}")
        draft = (
            f"Introduction\nThis section introduces {question}.\n\n"
            f"Explanation\nBased on research: {research}\n\n"
            f"Conclusion\nThis concludes the topic of {question}."
        )
        
    state.update("draft", draft)
    log("Writer", "Draft generation completed.")
    
    return draft
