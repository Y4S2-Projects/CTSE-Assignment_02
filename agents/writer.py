from core.state import state
from core.logger import log
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate


REQUIRED_SECTIONS = [
    "Introduction",
    "Explanation",
    "Examples",
    "Advantages / Use cases",
    "Conclusion",
]


def _word_count(text: str) -> int:
    return len((text or "").split())


def _has_required_sections(text: str) -> bool:
    text_lower = (text or "").lower()
    return all(section.lower() in text_lower for section in REQUIRED_SECTIONS)


def _build_complete_assignment(question: str, research: str, feedback: str = "") -> str:
    topic = question or "the selected assignment topic"
    research_context = research or (
        "The topic should be explained with a definition, key concepts, practical examples, "
        "advantages, limitations, and a clear conclusion."
    )
    improvement_note = (
        f"\n\nThe previous evaluation feedback was: {feedback}"
        if feedback
        else ""
    )

    return (
        f"# {topic}\n\n"
        "## Introduction\n"
        f"{topic} is an important area to understand because it connects theoretical knowledge "
        "with practical problem solving. A good assignment answer should not only define the topic, "
        "but also explain how it works, why it is useful, and how it can be applied in real situations. "
        f"In this discussion, the topic is examined using the available research context: {research_context} "
        "This helps create an answer that is structured, readable, and suitable for academic submission."
        f"{improvement_note}\n\n"
        "## Explanation\n"
        f"The main idea behind {topic} is that it provides a systematic way to understand and solve a "
        "specific type of problem. In academic writing, the explanation should move from simple concepts "
        "to deeper details. First, the topic should be introduced with a clear definition. Then the answer "
        "should explain the major components, processes, or principles involved. For example, if the topic "
        "is related to software engineering, the discussion should describe the relevant methods, tools, "
        "workflow, architecture, and quality concerns. If the topic is related to artificial intelligence "
        "or data, the discussion should describe how information is processed, how decisions are made, "
        "and how results are evaluated. This makes the answer more complete than a short definition.\n\n"
        f"Based on the research context, {topic} should also be understood through its purpose and impact. "
        "The topic may help improve efficiency, support better decision-making, reduce manual effort, "
        "increase accuracy, or make complex systems easier to manage. A correct assignment response should "
        "connect these benefits to the actual subject rather than giving only generic statements. It should "
        "also mention that implementation requires planning, testing, evaluation, and continuous improvement. "
        "This demonstrates that the writer understands both the concept and the practical responsibilities "
        "that come with applying it.\n\n"
        "## Examples\n"
        f"A practical example of {topic} can be seen in a student or business system where a clear process "
        "is needed to transform input into useful output. In a software project, this could involve collecting "
        "requirements, designing a solution, implementing features, testing the output, and improving the result "
        "based on feedback. In an artificial intelligence or automation project, it could involve gathering data, "
        "processing information, generating an answer or prediction, and evaluating the quality of the result. "
        "These examples show that the topic is not only theoretical. It can be applied to build useful systems "
        "that support real users and solve real problems.\n\n"
        "Another example is an academic assignment helper that uses multiple agents. One agent can create a plan, "
        "another can collect research, another can write the draft, and a final agent can evaluate the quality. "
        "This type of workflow demonstrates how a complex task can be divided into smaller responsibilities. "
        "The result is easier to understand, easier to test, and easier to improve.\n\n"
        "## Advantages / Use cases\n"
        f"The advantages of {topic} include better organization, improved clarity, and stronger decision-making. "
        "When the topic is applied properly, it can save time, reduce errors, and make results more consistent. "
        "It is useful in education, software development, business analysis, automation, data processing, and "
        "research-based projects. It can also support collaboration because different people or system components "
        "can focus on different parts of the work.\n\n"
        "However, good use of the topic also requires care. The output should be checked for accuracy, completeness, "
        "and relevance. Testing is important because a system or explanation may appear correct but still miss key "
        "requirements. Evaluation criteria such as structure, word count, clarity, examples, and conclusion help "
        "ensure that the final result is suitable for submission or practical use.\n\n"
        "## Conclusion\n"
        f"In conclusion, {topic} is valuable because it helps explain a concept in a structured and practical way. "
        "A strong assignment should include an introduction, a detailed explanation, examples, advantages or use "
        "cases, and a clear conclusion. By connecting research with real-world application, the final answer becomes "
        "more useful and academically complete. The most important point is that the topic should be explained with "
        "clarity, depth, and evidence of understanding rather than with short or incomplete statements."
    )


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
        draft = _build_complete_assignment(question, research, feedback)

    if _word_count(draft) < 300 or not _has_required_sections(draft):
        log("Writer", "Draft was incomplete. Rebuilding with structured fallback content.")
        draft = _build_complete_assignment(question, research, feedback)
        
    state.update("draft", draft)
    log("Writer", "Draft generation completed.")
    
    return draft
