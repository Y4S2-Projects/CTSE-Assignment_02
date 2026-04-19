# Smart Assignment Helper - Multi-Agent System

This is a production-level Python project that utilizes a Multi-Agent System (MAS) to help generate, research, and evaluate assignments. All processing runs fully locally using Ollama.

## Architecture Diagram

```
[User Input] --> (Coordinator Agent)
                        |
                        v
                 (Researcher Agent) <--> [Search Tool]
                        |
                        v
                   (Writer Agent) <--> [File Tool]
                        |
                        v
                 (Evaluator Agent) <--> [Eval Tool]
                        |
                        v
                 [Final Output]
```

## Agents
1. **Coordinator**: Breaks the user's question down into a manageable plan.
2. **Researcher**: Looks up information based on the plan using search tools.
3. **Writer**: Writes the actual assignment with Introduction, Explanation, and Conclusion.
4. **Evaluator**: Evaluates the written draft to ensure quality and structure.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install and Run Ollama
You need Ollama installed to run the local language models.
1. Download Ollama from [ollama.com](https://ollama.com/)
2. Run the Ollama server:
   ```bash
   ollama serve
   ```
3. Pull the llama3 model:
   ```bash
   ollama pull llama3
   ```

### 3. Run the System
You can run the standard pipeline:
```bash
python pipeline.py
```

Or you can run the LangGraph version of the workflow:
```bash
python langgraph_pipeline.py
```

You can also open the `main.ipynb` in Jupyter Notebook to run it interactively.

### 4. Run Tests
```bash
python -m unittest discover tests/
```

## Advanced Features
- **LangGraph Integration**: An alternative graph-based pipeline workflow is available in `langgraph_pipeline.py`.
- **Advanced Logging**: All steps and LLM outputs are captured locally in `logs.txt` with timestamps.
- **Error Handling**: Native fallbacks ensure the system won't crash even if Ollama fails to respond, allowing continuous validation of the overall multi-agent flow.
