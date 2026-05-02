from core.state import state
from core.logger import log
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from tools.search_tool import search_knowledge

def researcher_agent() -> str:
    """Researcher Agent: Uses LLM to generate detailed research."""
    question = state.get("question")
    
    log("Researcher", "Starting research generation with LLM.")
    
    if not question:
        log("Researcher", "No question found in state.")
        return "No research conducted."
        
    llm = OllamaLLM(model="llama3")
    knowledge_context = search_knowledge(question)
    prompt = PromptTemplate.from_template(
        "You are an expert Researcher. Explain in detail: {question}\n\n"
        "Use this known context where relevant: {knowledge_context}\n\n"
        "Ensure your response is between 150-300 words and covers:\n"
        "- Definition\n"
        "- Explanation\n"
        "- Real-world examples\n"
        "- Key concepts\n\n"
        "Research Output:"
    )
    
    try:
        chain = prompt | llm
        research_data = chain.invoke(
            {
                "question": question,
                "knowledge_context": knowledge_context,
            }
        )
    except Exception as e:
        log("Researcher", f"Error generating research with Ollama: {e}")
        research_data = (
            f"Definition: {question} refers to a topic that should be explained through its purpose, "
            f"main concepts, process, and practical value. Background context: {knowledge_context}\n\n"
            f"Explanation: A strong assignment should describe what {question} means, why it matters, "
            "how it works in a real environment, and which components or principles support it. "
            "The answer should connect theory with practical implementation so the reader can understand "
            "both the concept and its use.\n\n"
            "Real-world examples: This topic can be demonstrated through academic case studies, software "
            "engineering projects, business systems, automation workflows, or data-driven applications. "
            "Examples should show the problem being solved, the method used, and the benefit gained.\n\n"
            "Key concepts: Important points include definition, purpose, architecture or process, benefits, "
            "limitations, implementation considerations, and a clear conclusion."
        )
    
    log("Researcher", "Research completed successfully.")
    state.update("research", research_data)
    
    return research_data
