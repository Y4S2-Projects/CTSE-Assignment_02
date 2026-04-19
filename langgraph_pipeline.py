from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from core.state import state as global_state
from core.logger import log
from agents.coordinator import coordinator_agent
from agents.researcher import researcher_agent
from agents.writer import writer_agent
from agents.evaluator import evaluator_agent

# Define the state for LangGraph
class AgentState(TypedDict):
    question: str
    plan: str
    research: str
    draft: str
    evaluation: Dict[str, Any]

def coordinator_node(state: AgentState):
    plan = coordinator_agent(state["question"])
    return {"plan": plan}

def researcher_node(state: AgentState):
    research = researcher_agent()
    return {"research": research}

def writer_node(state: AgentState):
    draft = writer_agent()
    return {"draft": draft}

def evaluator_node(state: AgentState):
    evaluation = evaluator_agent()
    return {"evaluation": evaluation}

def build_langgraph():
    """Builds and returns the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("evaluator", evaluator_node)
    
    # Add edges
    workflow.set_entry_point("coordinator")
    workflow.add_edge("coordinator", "researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "evaluator")
    workflow.add_edge("evaluator", END)
    
    return workflow.compile()

def run_langgraph_system(question: str) -> AgentState:
    """Runs the multi-agent system using LangGraph.
    
    Args:
        question (str): The question to answer.
        
    Returns:
        AgentState: The final state of the LangGraph execution.
    """
    log("System (LangGraph)", f"--- Starting LangGraph pipeline for question: '{question}' ---")
    
    # Reset global state to ensure clean run
    global_state.state = {
        "question": None,
        "plan": None,
        "research": None,
        "draft": None,
        "evaluation": None
    }
    
    app = build_langgraph()
    initial_state = AgentState(
        question=question,
        plan="",
        research="",
        draft="",
        evaluation={}
    )
    
    final_state = app.invoke(initial_state)
    
    log("System (LangGraph)", "--- LangGraph Pipeline execution finished ---")
    
    return final_state

if __name__ == "__main__":
    # Get the question from the user interactively
    question = input("\n📝 Enter your question: ")
    
    result = run_langgraph_system(question)
    print("\nFINAL ANSWER:\n")
    print(result.get("draft", ""))
    print("\nEVALUATION:\n", result.get("evaluation", {}))
