from dotenv import load_dotenv
load_dotenv()

import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()




def chat_with_query(messages, model):
    """
    Uses the Groq API to generate a chat response based on a list of messages.
    Each message is a dict with 'role' in ['system', 'user', 'assistant']
    and a 'content' string.
    """
    client = Groq()
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model
    )
    return chat_completion.choices[0].message.content


