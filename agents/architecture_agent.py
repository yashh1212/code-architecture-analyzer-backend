# agents/architecture_agent.py

def build_prompt(context: str, question: str):
    return f"""
You are a senior software architect.
Answer using ONLY the given code context.
Mention files and reasoning.

Context:
{context}

Question:
{question}
"""
