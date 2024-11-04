import os
from openai import OpenAI
from lib.storage import get_llm_system_message

openai_client = OpenAI()

def generate_ebook(transcript):
    system_message = get_llm_system_message()
    model = os.environ['OPENAI_MODEL']
    user_message = f"I have a transcript I need you to convert to an Ebook: {transcript}"

    completion = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    return completion.choices[0].message.content
    