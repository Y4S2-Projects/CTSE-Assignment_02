import streamlit as st
import sys
import os

# Ensure the core and agents packages can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pipeline import run_system
from core.state import state

# Configure the Streamlit page
st.set_page_config(page_title="Smart Assignment Helper", page_icon="🤖", layout="wide")

# UI Headers
st.title("🤖 Smart Assignment Helper")
st.markdown("### Multi-Agent System Dashboard")
st.markdown("Enter your assignment question below, and the **Coordinator, Researcher, Writer, and Evaluator** agents will work together to generate a high-quality response using local AI.")

# User Input
question = st.text_area("📝 Enter your question here:", height=100, placeholder="e.g., Explain the fundamentals of machine learning...")

# Run Button
if st.button("🚀 Run Multi-Agent System", type="primary"):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Agents are working... (This may take a minute depending on your computer's speed)"):
            try:
                # Reset global state for a clean run if necessary
                state.state = {
                    "question": None,
                    "plan": None,
                    "research": None,
                    "draft": None,
                    "evaluation": None
                }
                
                # Run the pipeline
                final_answer, evaluation, full_state = run_system(question)
                
                st.success("✅ Assignment generation complete!")
                
                # Display Results in Tabs
                tab1, tab2, tab3 = st.tabs(["📄 Final Answer", "📊 Evaluation", "🧠 Internal Agent State"])
                
                with tab1:
                    st.markdown("### Generated Assignment")
                    st.write(final_answer)
                    
                with tab2:
                    st.markdown("### Evaluation Results")
                    score = evaluation.get("score", 0)
                    status = evaluation.get("status", "Unknown")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Score", f"{score}/100")
                    
                    # Color code the status
                    if status == "Passed":
                        col2.metric("Status", status, "Passed")
                        st.balloons()
                    else:
                        col2.metric("Status", status, "-Failed")
                        
                with tab3:
                    st.markdown("### Agent Reasoning State")
                    st.markdown("**1. Coordinator Agent (Plan):**")
                    st.info(full_state.get("plan", "No plan generated."))
                    
                    st.markdown("**2. Researcher Agent (Findings):**")
                    st.info(full_state.get("research", "No research found."))
                    
                    st.markdown("**3. Writer Agent (Initial Draft):**")
                    with st.expander("View Initial Draft"):
                        st.write(full_state.get("draft", "No draft generated."))
                        
            except Exception as e:
                st.error(f"An error occurred during execution: {str(e)}")

st.markdown("---")
st.caption("Powered by locally hosted Llama 3 via Ollama | Multi-Agent Architecture")
