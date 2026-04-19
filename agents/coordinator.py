from core.state import state
from core.logger import log
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def coordinator_agent(question: str) -> str:
    """Coordinator Agent: Breaks down the task into a plan.
    
    Args:
        question (str): The user's question.
        
    Returns:
        str: The generated plan.
    """
    log("Coordinator", f"Received question: {question}")
    state.update("question", question)
    
    llm = OllamaLLM(model="llama3")
    prompt = PromptTemplate.from_template(
        "You are a Coordinator Agent. Your task is to break down the following question into a 3-step research and writing plan.\n\nQuestion: {question}\n\nPlan:"
    )
    
    log("Coordinator", "Generating plan...")
    try:
        chain = prompt | llm
        plan = chain.invoke({"question": question})
    except Exception as e:
        log("Coordinator", f"Error connecting to Ollama: {e}")
        plan = f"Step 1: Research '{question}'. Step 2: Write Introduction and Explanation. Step 3: Write Conclusion."
        
    state.update("plan", plan)
    log("Coordinator", f"Plan generated:\n{plan}")
    return plan
