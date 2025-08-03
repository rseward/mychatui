#!/usr/bin/env python

import os
import aisuite as ai
from aisuite.providers.googlegenai_provider import GoogleGenaiProvider

provider = GoogleGenaiProvider()
gemini_models = provider.list_models()

print(f"gemini models: {gemini_models}")

# Initialize the AI client for accessing the language model
client = ai.Client()

q1 = "Explain the impact of Federal Department of Education Policy impact on local American schools."
q2 = "Why is the sky blue"

# Define a conversation with a system message and a user message
messages = [
    {"role": "system", "content": "You are a helpful agent, who answers with brevity."},
    {"role": "user", "content": q2},
]

models = ["googlegenai:models/gemini-1.5-flash"]

models = [
    "googlegenai:models/gemini-1.5-flash",
    "ollama:qwen2.5:latest",
    "ollama:llama3.2:1b",
    "ollama:gemma3:latest",
    "openai:mistralai/mistral-small-3.1-24b-instruct:free",
    # "ollama:llama3:8b-instruct-q8_0",
    # "ollama:llama3.1:latest",
    # "googlegenai:models/gemini-1.5-flash"
]


# Request a response from the model
for model in models:
    print(f"= {model} says ... =")
    base_url = None
    if "openai" in model:
        base_url = os.getenv("OPENAI_API_URL")
    response = None
    if base_url is not None:
        response = client.chat.completions.create(
            model=model, messages=messages, base_url=base_url
        )
    else:
        response = client.chat.completions.create(model=model, messages=messages)
    # Print the model's response
    print(response.choices[0].message.content)
    #import json

    #print(json.dumps(response, indent=2))
    print("")
