def search_knowledge(query: str) -> str:
    """Simulates a knowledge base search.
    
    Args:
        query (str): The search query.
        
    Returns:
        str: The search results.
    """
    knowledge_base = {
        "machine learning": "Machine learning is a field of study in artificial intelligence concerned with the development and study of statistical algorithms that can learn from data and generalize to unseen data, and thus perform tasks without explicit instructions.",
        "neural networks": "Neural networks are computing systems inspired by the biological neural networks that constitute animal brains.",
        "default": "General research content regarding the query topic has been aggregated. It includes an overview of the foundational concepts and state-of-the-art developments."
    }
    
    query_lower = query.lower()
    for key, info in knowledge_base.items():
        if key != "default" and key in query_lower:
            return info
            
    return knowledge_base["default"]
