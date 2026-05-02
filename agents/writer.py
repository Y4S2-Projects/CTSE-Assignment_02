from core.state import state
from core.logger import log
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def writer_agent(feedback: str = "") -> str:
    """Writer Agent: Generates content based on research and optional feedback."""
    question = state.get("question")
    research = state.get("research")
    
    if feedback:
        log("Writer", f"Refining draft based on feedback: {feedback}")
        system_instruction = (
            "You are an academic Writer Agent. Improve the previous answer based on the evaluation feedback below.\n"
            f"Feedback: {feedback}\n"
        )
    else:
        log("Writer", "Starting draft generation based on research.")
        system_instruction = "You are an academic Writer Agent."

    llm = OllamaLLM(model="llama3")
    prompt = PromptTemplate.from_template(
        "{system_instruction}\n\n"
        "Write a detailed academic answer for the following:\n\n"
        "Topic: {question}\n"
        "Research Context: {research}\n\n"
        "Structure:\n"
        "- Introduction\n"
        "- Explanation\n"
        "- Examples\n"
        "- Advantages / Use cases\n"
        "- Conclusion\n\n"
        "Ensure clarity, depth, and completeness. Minimum 300-500 words.\n"
        "Structured Output:"
    )
    
    try:
        chain = prompt | llm
        draft = chain.invoke({
            "system_instruction": system_instruction,
            "question": question, 
            "research": research
        })
    except Exception as e:
        log("Writer", f"Error generating draft with Ollama: {e}")
        draft = (
            f"Introduction\nThis section introduces {question}.\n\n"
            f"Explanation\nBased on research: {research}\n\n"
            f"Examples\nExamples of {question}.\n\n"
            f"Advantages / Use cases\nAdvantages of {question}.\n\n"
            f"Conclusion\nThis concludes the topic of {question}."
        )
        
    state.update("draft", draft)
    log("Writer", "Draft generation completed.")
    
    return draft
