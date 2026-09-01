from groq import Groq
from src.core.config import config

client = Groq(api_key=config.GROQ_API_KEY)


def call_llm(prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
    """
    Sends a prompt to our configured LLM and returns the plain text response.
    
    This is the single place all agents go through to talk to the LLM.
    If we ever switch models or providers again (like we just had to,
    thanks to the deprecation), this is the only file that changes —
    every agent using call_llm() keeps working without modification.
    
    Args:
        prompt: the actual question/task for the LLM
        system_prompt: sets the LLM's role/behavior for this call
    
    Returns: the LLM's text response as a plain string
    """
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content