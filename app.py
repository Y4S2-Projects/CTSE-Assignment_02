import streamlit as st
import sys
import os
import time

# Ensure the core and agents packages can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pipeline import run_system
from core.state import state

# 1. MODERN LAYOUT
st.set_page_config(
    page_title="Smart Assignment Helper",
    page_icon="🧠",
    layout="wide"
)

# 7. SIDEBAR (PROFESSIONAL TOUCH)
st.sidebar.title("⚙️ Settings")
selected_model = st.sidebar.selectbox("Model Selection", ["phi3", "llama3"], index=1)
show_logs = st.sidebar.toggle("Show Debug Logs", value=False)
st.sidebar.markdown("---")
st.sidebar.info("This system uses a Multi-Agent architecture with local LLM via Ollama.")

# 2. HEADER SECTION
st.title("🧠 Multi-Agent AI Assignment Generator")
st.subheader("Powered by Coordinator, Researcher, Writer & Evaluator Agents (Ollama Local AI)")
st.divider()

# 3. INPUT SECTION (TOP CARD)
with st.container():
    question = st.text_area(
        "📝 Assignment Topic:",
        height=150,
        placeholder="Enter your assignment question here..."
    )
    
    st.write("") # Spacing
    generate_btn = st.button("🚀 Generate Answer", type="primary", use_container_width=True)

st.write("") # Spacing

# Main Execution Logic
if generate_btn:
    # 10. ERROR HANDLING
    if not question.strip():
        st.warning("⚠️ Please enter an assignment question to generate an answer.")
    else:
        # Reset state for a fresh execution
        state.state = {
            "question": None,
            "plan": None,
            "research": None,
            "draft": None,
            "evaluation": None
        }
        
        start_time = time.time()
        
        # 4. LOADING ANIMATION
        with st.spinner("Agents are working..."):
            try:
                # 5. AGENT WORKFLOW VISUALIZATION (In-Progress)
                progress_placeholder = st.empty()
                with progress_placeholder.container():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.info("⏳ Coordinator → Planning")
                    with col2:
                        st.info("⏳ Researcher → Data Collection")
                    with col3:
                        st.info("⏳ Writer → Content Generation")
                    with col4:
                        st.info("⏳ Evaluator → Quality Check")
                
                # Execute Pipeline (Backend untouched)
                final_answer, evaluation, full_state = run_system(question)
                
                # Update Workflow Visualization to Success
                with progress_placeholder.container():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.success("✔ Coordinator → Planning")
                    with col2:
                        st.success("✔ Researcher → Data Collection")
                    with col3:
                        st.success("✔ Writer → Content Generation")
                    with col4:
                        st.success("✔ Evaluator → Quality Check")

                execution_time = time.time() - start_time
                st.success(f"✅ Assignment successfully generated in {execution_time:.2f} seconds!")
                
                st.write("") # Spacing
                
                # 6. TABS FOR OUTPUT
                tabs = st.tabs([
                    "📄 Final Answer", 
                    "📊 Evaluation", 
                    "🧠 Agent State"
                ])
                
                # 📄 TAB 1: FINAL ANSWER
                with tabs[0]:
                    st.markdown("### 🎓 Generated Assignment")
                    st.write("")
                    st.markdown(final_answer)
                    
                # 📊 TAB 2: EVALUATION
                with tabs[1]:
                    st.markdown("### 📊 Evaluation Metrics")
                    status = evaluation.get("status", "Unknown")
                    feedback = evaluation.get("feedback", "No feedback provided.")
                    
                    col_stat, col_emp = st.columns([1, 3])
                    with col_stat:
                        if status == "Good":
                            st.success(f"**Status:** {status} ✅")
                        else:
                            st.error(f"**Status:** {status} ⚠️")
                        
                    st.markdown("#### 📝 Evaluator Feedback:")
                    if status == "Good":
                        st.success(feedback)
                    else:
                        st.warning(feedback)
                    
                # 🧠 TAB 3: AGENT STATE
                with tabs[2]:
                    st.markdown("### 🧠 Full Internal State")
                    st.json(full_state)
                    
            except Exception as e:
                st.error(f"❌ An error occurred during system execution: {str(e)}")

# 8. FOOTER
st.write("")
st.write("")
st.divider()
st.caption("Developed using Multi-Agent AI | SLIIT Assignment | Powered by Ollama")
